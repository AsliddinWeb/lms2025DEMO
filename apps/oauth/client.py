import requests
from urllib.parse import urlencode


class oAuth2Client:
    def __init__(self, client_id, client_secret, redirect_uri, authorize_url, token_url, resource_owner_url):
        self.client_secret = client_secret
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.resource_owner_url = resource_owner_url

    def get_authorization_url(self):
        payload = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
        }
        # ⚠️ authorize bosqichida client_secret yuborilmaydi
        url = self.authorize_url + "?" + urlencode(payload)
        return url

    def get_access_token(self, auth_code):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(self.token_url, data=payload, headers=headers)

        print("DEBUG TOKEN STATUS:", response.status_code)
        print("DEBUG TOKEN HEADERS:", response.headers)
        print("DEBUG TOKEN BODY:", response.text)

        try:
            return response.json()
        except Exception as e:
            return {
                "error": "invalid_json",
                "details": str(e),
                "raw_response": response.text
            }

    def get_user_details(self, access_token):
        response = requests.get(
            self.resource_owner_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        return response.json()
