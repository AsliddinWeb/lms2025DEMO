import requests
from django.conf import settings
from datetime import datetime

def refresh_access_token(request):
    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return None

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
    }
    response = requests.post(settings.ACCESS_TOKEN_URL, data=data)
    if response.status_code == 200:
        tokens = response.json()
        request.session['access_token'] = tokens['access_token']
        request.session['refresh_token'] = tokens.get('refresh_token', refresh_token)
        request.session['expires_in'] = tokens.get('expires_in')
        request.session['token_created_at'] = datetime.now().timestamp()
        return tokens['access_token']
    return None


def get_student_subjects(request):
    access_token = request.session.get('student_api_token')
    expires_in = request.session.get('expires_in')
    created_at = request.session.get('token_created_at')

    # token muddati tugaganini tekshirish
    if access_token and expires_in and created_at:
        if datetime.now().timestamp() - created_at > expires_in:
            access_token = refresh_access_token(request)

    if not access_token:
        return {"error": "Access token not found or expired"}

    url = f"https://student.xiuedu.uz/rest/v1/education/subjects"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}


def get_my_info(request):
    access_token = request.session.get('student_api_token')
    expires_in = request.session.get('expires_in')
    created_at = request.session.get('token_created_at')

    # token muddati tugaganini tekshirish
    if access_token and expires_in and created_at:
        if datetime.now().timestamp() - created_at > expires_in:
            access_token = refresh_access_token(request)

    if not access_token:
        return {"error": "Access token not found or expired"}

    url = f"https://student.xiuedu.uz/rest/v1/account/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}


def get_subject_detail(request, subject, semester):
    access_token = request.session.get('student_api_token')
    expires_in = request.session.get('expires_in')
    created_at = request.session.get('token_created_at')

    # Token muddati tugaganini tekshirish
    if access_token and expires_in and created_at:
        try:
            created_at = float(created_at)  # sessionda string saqlangan bo‘lishi mumkin
        except (ValueError, TypeError):
            created_at = 0

        if datetime.now().timestamp() - created_at > int(expires_in):
            access_token = refresh_access_token(request)

    if not access_token:
        return {"error": "Access token not found or expired"}

    # 🔥 To‘g‘ri endpoint (misol uchun)
    url = "https://student.xiuedu.uz/rest/v1/education/subject"

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"subject": subject, "semester": semester}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}

def get_subject_resources(request, subject, semester):
    access_token = request.session.get('student_api_token')
    expires_in = request.session.get('expires_in')
    created_at = request.session.get('token_created_at')

    # Token muddati tugaganini tekshirish
    if access_token and expires_in and created_at:
        try:
            created_at = float(created_at)  # sessionda string saqlangan bo‘lishi mumkin
        except (ValueError, TypeError):
            created_at = 0

        if datetime.now().timestamp() - created_at > int(expires_in):
            access_token = refresh_access_token(request)

    if not access_token:
        return {"error": "Access token not found or expired"}

    # 🔥 To‘g‘ri endpoint (misol uchun)
    url = "https://student.xiuedu.uz/rest/v1/education/resources"

    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"subject": subject, "semester": semester}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": str(e)}