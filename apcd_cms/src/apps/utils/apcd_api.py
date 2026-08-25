import os

import httpx
import hvac
from django.conf import settings


VAULT_URL = 'https://vault.txapcd.org'
VAULT_ROLE = getattr(settings, 'VAULT_ROLE', '')
VAULT_SECRET = getattr(settings, 'VAULT_SECRET', '')
API_URL = 'https://apcd-etl-dev.txapcd.org'
API_USER = 'gedmonds'


def get_api_key_from_vault() -> str:
    """Get the API key from HashiCorp Vault."""
    vault = hvac.Client(url=VAULT_URL)
    vault.auth.approle.login(role_id=VAULT_ROLE, secret_id=VAULT_SECRET, use_token=True)
    vault_secret = vault.secrets.kv.v2.read_secret(path='keys/api-key', mount_point='apcd')
    print('api key:',vault_secret['data']['data']['api-key'])
    return vault_secret['data']['data']['api-key']


def login(username: str) -> None:
    API_KEY = get_api_key_from_vault()
    """Login and return api access token."""
    login_data = {'username': username, 'password': API_KEY}
    response = api_client(url='/auth/access-token', method='post', data=login_data)
    print('\nPOST request status:', response.status_code)
    response.raise_for_status()
    token_response = response.json()
    print('Created resource:', token_response)
    return token_response['access_token']


def ping(client: httpx.Client) -> None:
    """Ping the API to check connectivity."""
    response = client.get('')
    print('\nGET /root request status:', response.status_code)
    response.raise_for_status()
    print('Ping Response:', response.json())


def status(client: httpx.Client) -> None:
    """Check API status."""
    response = client.get('/status')
    print('\nGET /status request status:', response.status_code)
    response.raise_for_status()
    print('API Status:', response.json())

def me(client: httpx.Client) -> None:
    """Get current user information."""
    response = client.get('/users/me')
    print('\nGET /users/me request status:', response.status_code)
    response.raise_for_status()
    print('Current User Info:', response.json())


def sub_exc(token: str) -> None:
    """Get submitter exceptions information."""
    response = api_client(url='/submitter-exceptions/paged_view?page=1&per_page=50', method='get', token=token)
    print('\nGET /submitter-exceptions request status:', response.status_code)
    response.raise_for_status()
    print('Submitter Exceptions Data:', response.json())
    return response.json()


def api_client(url: str, method: str, data: object = None, token: str = None) -> None:
    response = {}
    try:
        with httpx.Client(timeout=5.0, base_url=API_URL) as client:
            if not 'auth' in url:
                client.headers.update({'Authorization': f'Bearer {token}'})
            if method == 'get':
                response = client.get(url)
            if method == 'post':
                response = client.post(url, data=data)
    except httpx.RequestError as exc:
        print(f'An error occurred while requesting {exc.request.url!r}: {exc}')
        response = exc.response
    except httpx.HTTPStatusError as exc:
        print(f'Error response {exc.response.status_code} while requesting {exc.request.url!r}')
        response = exc.response
    return response


if __name__ == '__main__':
    main()