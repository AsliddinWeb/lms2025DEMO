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
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
        }

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

        print(f"POST Request to: {self.token_url}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(self.token_url, data=payload, timeout=30)
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            print(f"Response Text: {response.text[:500]}")  # Birinchi 500 belgini ko'rsatish

            if response.status_code != 200:
                return {
                    'error': f'HTTP {response.status_code}',
                    'message': response.text
                }

            return response.json()

        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw response: {response.text}")
            return {
                'error': 'Invalid JSON response',
                'raw_response': response.text,
                'status_code': response.status_code
            }
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout'}
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            return {'error': str(e)}

    def get_user_details(self, access_token):
        print(f"GET Request to: {self.resource_owner_url}")
        print(f"Access Token: {access_token[:20]}...")

        try:
            response = requests.get(
                self.resource_owner_url,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=30
            )

            print(f"User Details Response Status: {response.status_code}")
            print(f"User Details Response: {response.text[:500]}")

            if response.status_code != 200:
                return None

            return response.json()

        except requests.exceptions.JSONDecodeError as e:
            print(f"JSON Decode Error in user details: {e}")
            print(f"Raw response: {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in user details: {e}")
            return None
