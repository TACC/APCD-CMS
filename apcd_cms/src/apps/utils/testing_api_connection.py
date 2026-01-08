import os
import httpx

from hvac import Client
from django.conf import settings

print("testing api connection")
VAULT_ROLE = getattr(settings, 'VAULT_ROLE', '')
VAULT_SECRET = getattr(settings, 'VAULT_SECRET', '')

client = Client(url='https://vault.txapcd.org')
client.auth.approle.login(role_id=VAULT_ROLE, secret_id=VAULT_SECRET, use_token=True)
vault_secret = client.secrets.kv.v2.read_secret(path='keys/api-key', mount_point='apcd')

URL = 'https://apcd-etl-dev.txapcd.org'
USERNAME = 'test_submitter_user'
PASSWORD = vault_secret['data']['data']['api-key']


def main():
     try:
         with httpx.Client(timeout=5.0, base_url=URL) as client:
             # Check connection without authentication
             response = client.get('/')
             print('GET request status:', response.status_code)
             response.raise_for_status()
             print('Response JSON:', response.json())

             # Login and set authorization header
             login_data = {'username': USERNAME, 'password': PASSWORD}
             response = client.post('/auth/access-token', data=login_data)
             print('\nPOST request status:', response.status_code)
             response.raise_for_status()
             token_response = response.json()
             print('Created resource:', token_response)
             auth_header = {'Authorization': f'Bearer {token_response["access_token"]}'}
             client.headers.update(auth_header)

             # Example GET request with authentication
             response = client.get('/users?limit=2')
             print('\nGET request status with auth:', response.status_code)
             response.raise_for_status()
             print('Users:', response.json())

     except httpx.RequestError as exc:
         print(f'An error occurred while requesting {exc.request.url!r}: {exc}')

     except httpx.HTTPStatusError as exc:
        print(f'Error response {exc.response.status_code} while requesting {exc.request.url!r}')

if __name__ == '__main__':
     main()
