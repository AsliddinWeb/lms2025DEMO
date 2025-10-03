import requests
from datetime import datetime
from django.shortcuts import redirect, render
from django.conf import settings
from django.views import View
from django.contrib.auth import login, logout
from django.db import transaction
from django.core.files.base import ContentFile

from django.http import JsonResponse

# Models
from apps.account.models import User, StudentProfile, TeacherProfile  # <-- models to'g'ri import qilingan


# OAuth2 client
from .client import oAuth2Client


class StudentAuthLoginView(View):
    def get(self, request):
        request.session['user_type'] = 'student'  # sessionga saqlaymiz

        client = oAuth2Client(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirect_uri=settings.REDIRECT_URI,
            authorize_url=settings.AUTHORIZE_URL,
            token_url=settings.ACCESS_TOKEN_URL,
            resource_owner_url=settings.RESOURCE_OWNER_URL
        )
        authorization_url = client.get_authorization_url()
        return redirect(authorization_url)


class TeacherAuthLoginView(View):
    def get(self, request):
        request.session['user_type'] = 'teacher'

        client = oAuth2Client(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirect_uri=settings.REDIRECT_URI,
            authorize_url=settings.TEACHER_AUTHORIZE_URL,
            token_url=settings.TEACHER_ACCESS_TOKEN_URL,
            resource_owner_url=settings.TEACHER_RESOURCE_OWNER_URL
        )
        authorization_url = client.get_authorization_url()
        return redirect(authorization_url)



class AuthCallbackView(View):
    def get(self, request):
        print('++++++++++++++++++++++++++++++++++')
        code = request.GET.get('code')
        user_type = request.session.get('user_type', 'student')  # default student

        if not code:
            return render(request, 'error.html', {'error': 'Authorization code is missing!'})

        # Student yoki Teacher uchun mos OAuth URL lar
        if user_type == 'teacher':
            authorize_url = settings.TEACHER_AUTHORIZE_URL
            token_url = settings.TEACHER_ACCESS_TOKEN_URL
            resource_owner_url = settings.TEACHER_RESOURCE_OWNER_URL
        else:
            authorize_url = settings.AUTHORIZE_URL
            token_url = settings.ACCESS_TOKEN_URL
            resource_owner_url = settings.RESOURCE_OWNER_URL

        # OAuth client
        client = oAuth2Client(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirect_uri=settings.REDIRECT_URI,
            authorize_url=authorize_url,
            token_url=token_url,
            resource_owner_url=resource_owner_url
        )

        # access_token_response = client.get_access_token(code)

        # full_info = {}
        # if 'access_token' in access_token_response:
        #     access_token = access_token_response['access_token']
        #     user_details = client.get_user_details(access_token)
        #     full_info['details'] = user_details
        #     full_info['token'] = access_token
        #     return JsonResponse(full_info)
        # else:
        #     return JsonResponse(
        #         {
        #             'status': False,
        #             'error': 'Failed to obtain access token'
        #         },
        #         status=400
        #     )

        # Access token olish
        access_token_response = client.get_access_token(code)
        print(access_token_response)

        if 'access_token' not in access_token_response:
            return render(request, 'error.html', {'error': 'Failed to obtain access token'})

        access_token = access_token_response['access_token']
        user_details = client.get_user_details(access_token)

        if user_type == 'student':
            
            student_api_token = user_details['student_api_token']

            # Tokenni sessionga saqlaymiz (keyinchalik boshqa API chaqirish uchun)
            request.session['access_token'] = access_token
            request.session['student_api_token'] = student_api_token

            # Foydalanuvchi ma’lumotlarini olish
            user_details = client.get_user_details(access_token)
            if not user_details:
                return render(request, 'error.html', {'error': 'Failed to retrieve user details'})

        # User turiga qarab autentifikatsiya
        if user_type == 'teacher':
            user = self.authenticate_or_create_teacher(user_details)
        else:
            user = self.authenticate_or_create_student(user_details)

        if user:
            login(request, user)
            request.session.pop('user_type', None)  # sessiondan vaqtinchalik qiymatni o‘chiramiz
            return redirect('dashboard:home')

        return render(request, 'error.html', {'error': 'User authentication failed'})

    def authenticate_or_create_student(self, user_details):
        """Authenticate or create a student user."""
        user, created = User.objects.get_or_create(
            username=user_details['login'],
            defaults={
                'first_name': user_details.get('firstname', ''),
                'last_name': user_details.get('surname', ''),
                'role': User.Role.STUDENT,
            }
        )

        if created:
            with transaction.atomic():
                birth_date = self.parse_birth_date(user_details.get('birth_date', ''))
                picture_content = download_image(user_details.get('picture', ''))

                profile = StudentProfile.objects.create(
                    user=user,
                    first_name=user_details.get('firstname', ''),
                    last_name=user_details.get('surname', ''),
                    father_name=user_details.get('patronymic', ''),
                    phone=user_details.get('phone', ''),
                    birth_date=birth_date,
                )

                if picture_content:
                    file_name = user_details.get('picture', '').split("/")[-1]
                    profile.picture.save(file_name, picture_content, save=True)

        return user

    def authenticate_or_create_teacher(self, user_details):
        """Authenticate or create a teacher user."""
        user, created = User.objects.get_or_create(
            username=user_details['login'],
            defaults={
                'first_name': user_details.get('firstname', ''),
                'last_name': user_details.get('surname', ''),
                'role': User.Role.TEACHER,
            }
        )

        if created:
            with transaction.atomic():
                birth_date = self.parse_birth_date(user_details.get('birth_date', ''))
                picture_content = download_image(user_details.get('picture', ''))

                profile = TeacherProfile.objects.create(
                    user=user,
                    first_name=user_details.get('firstname', ''),
                    last_name=user_details.get('surname', ''),
                    father_name=user_details.get('patronymic', ''),
                    phone=user_details.get('phone', ''),
                    birth_date=birth_date
                )

                if picture_content:
                    file_name = user_details.get('picture', '').split("/")[-1]
                    profile.picture.save(file_name, picture_content, save=True)

        return user

    def parse_birth_date(self, birth_date_str):
        return datetime.strptime(birth_date_str, '%d-%m-%Y').date() if birth_date_str else None


def download_image(image_url):
    if image_url:
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                return ContentFile(response.content)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download image: {e}")
    return None


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('main:home_page')


class HomeView(View):
    def get(self, request):
        return render(request, 'home.html', {
            'user': request.user
        })
