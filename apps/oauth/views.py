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
from apps.account.models import User, StudentProfile, TeacherProfile

# OAuth2 client
from .client import oAuth2Client


class StudentAuthLoginView(View):
    def get(self, request):
        request.session['user_type'] = 'student'

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
        print('=' * 60)
        print('OAuth Callback Started')
        print('=' * 60)

        code = request.GET.get('code')
        user_type = request.session.get('user_type', 'student')

        print(f"User Type: {user_type}")
        print(f"Code exists: {bool(code)}")
        print(f"Code length: {len(code) if code else 0}")

        if not code:
            error_msg = 'Authorization code is missing!'
            print(f"ERROR: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

        # Student yoki Teacher uchun mos OAuth URL lar
        if user_type == 'teacher':
            authorize_url = settings.TEACHER_AUTHORIZE_URL
            token_url = settings.TEACHER_ACCESS_TOKEN_URL
            resource_owner_url = settings.TEACHER_RESOURCE_OWNER_URL
            print(f"Teacher URLs:")
            print(f"  - Authorize: {authorize_url}")
            print(f"  - Token: {token_url}")
            print(f"  - Resource Owner: {resource_owner_url}")
        else:
            authorize_url = settings.AUTHORIZE_URL
            token_url = settings.ACCESS_TOKEN_URL
            resource_owner_url = settings.RESOURCE_OWNER_URL
            print(f"Student URLs:")
            print(f"  - Authorize: {authorize_url}")
            print(f"  - Token: {token_url}")
            print(f"  - Resource Owner: {resource_owner_url}")

        print(f"Client ID: {settings.CLIENT_ID[:10]}...")
        print(f"Redirect URI: {settings.REDIRECT_URI}")

        # OAuth client
        client = oAuth2Client(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirect_uri=settings.REDIRECT_URI,
            authorize_url=authorize_url,
            token_url=token_url,
            resource_owner_url=resource_owner_url
        )

        # Access token olish
        try:
            print("Requesting access token...")
            access_token_response = client.get_access_token(code)
            print(f"Access Token Response: {access_token_response}")
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while getting access token: {str(e)}"
            print(f"EXCEPTION: {error_msg}")
            return JsonResponse({
                'error': 'Network error',
                'details': str(e),
                'user_type': user_type
            }, status=500)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"EXCEPTION: {error_msg}")
            return JsonResponse({
                'error': 'Unexpected error',
                'details': str(e),
                'user_type': user_type
            }, status=500)

        if 'access_token' not in access_token_response:
            print(f"ERROR: No access_token in response")
            print(f"Full response: {access_token_response}")
            return JsonResponse({
                'error': 'Failed to obtain access token',
                'details': access_token_response,
                'user_type': user_type,
                'token_url': token_url
            }, status=400)

        access_token = access_token_response['access_token']
        print(f"Access token received: {access_token[:20]}...")

        # User details olish
        try:
            print("Requesting user details...")
            user_details = client.get_user_details(access_token)
            print(f"User Details: {user_details}")
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while getting user details: {str(e)}"
            print(f"EXCEPTION: {error_msg}")
            return JsonResponse({
                'error': 'Network error while getting user details',
                'details': str(e),
                'user_type': user_type
            }, status=500)
        except Exception as e:
            error_msg = f"Unexpected error while getting user details: {str(e)}"
            print(f"EXCEPTION: {error_msg}")
            return JsonResponse({
                'error': 'Unexpected error while getting user details',
                'details': str(e),
                'user_type': user_type
            }, status=500)

        if not user_details:
            print("ERROR: Failed to retrieve user details")
            return JsonResponse({
                'error': 'Failed to retrieve user details',
                'user_type': user_type
            }, status=400)

        # Student uchun qo'shimcha token
        if user_type == 'student':
            student_api_token = user_details.get('student_api_token')
            if student_api_token:
                request.session['access_token'] = access_token
                request.session['student_api_token'] = student_api_token
                print(f"Student API token saved to session")
            else:
                print("WARNING: student_api_token not found in user_details")

        # User turiga qarab autentifikatsiya
        try:
            if user_type == 'teacher':
                print("Authenticating teacher...")
                user = self.authenticate_or_create_teacher(user_details)
            else:
                print("Authenticating student...")
                user = self.authenticate_or_create_student(user_details)
        except Exception as e:
            error_msg = f"Error during user authentication/creation: {str(e)}"
            print(f"EXCEPTION: {error_msg}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': 'User authentication failed',
                'details': str(e),
                'user_type': user_type
            }, status=500)

        if user:
            print(f"User authenticated successfully: {user.username}")
            login(request, user)
            request.session.pop('user_type', None)
            print("Redirecting to dashboard...")
            print('=' * 60)
            return redirect('dashboard:home')

        print("ERROR: User authentication failed")
        print('=' * 60)
        return JsonResponse({
            'error': 'User authentication failed',
            'user_type': user_type
        }, status=400)

    def authenticate_or_create_student(self, user_details):
        """Authenticate or create a student user."""
        print(f"Creating/getting student: {user_details.get('login')}")

        user, created = User.objects.get_or_create(
            username=user_details['login'],
            defaults={
                'first_name': user_details.get('firstname', ''),
                'last_name': user_details.get('surname', ''),
                'role': User.Role.STUDENT,
            }
        )

        print(f"Student user {'created' if created else 'found'}: {user.username}")

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
                print(f"Student profile created: {profile.id}")

                if picture_content:
                    file_name = user_details.get('picture', '').split("/")[-1]
                    profile.picture.save(file_name, picture_content, save=True)
                    print(f"Profile picture saved: {file_name}")

        return user

    def authenticate_or_create_teacher(self, user_details):
        """Authenticate or create a teacher user."""
        print(f"Creating/getting teacher: {user_details.get('login')}")

        user, created = User.objects.get_or_create(
            username=user_details['login'],
            defaults={
                'first_name': user_details.get('firstname', ''),
                'last_name': user_details.get('surname', ''),
                'role': User.Role.TEACHER,
            }
        )

        print(f"Teacher user {'created' if created else 'found'}: {user.username}")

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
                print(f"Teacher profile created: {profile.id}")

                if picture_content:
                    file_name = user_details.get('picture', '').split("/")[-1]
                    profile.picture.save(file_name, picture_content, save=True)
                    print(f"Profile picture saved: {file_name}")

        return user

    def parse_birth_date(self, birth_date_str):
        if birth_date_str:
            try:
                return datetime.strptime(birth_date_str, '%d-%m-%Y').date()
            except ValueError as e:
                print(f"Error parsing birth date '{birth_date_str}': {e}")
                return None
        return None


def download_image(image_url):
    if image_url:
        try:
            print(f"Downloading image: {image_url}")
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                print(f"Image downloaded successfully: {len(response.content)} bytes")
                return ContentFile(response.content)
            else:
                print(f"Failed to download image: HTTP {response.status_code}")
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
