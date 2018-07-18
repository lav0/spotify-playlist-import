import requests
import json
import requester
from oauth2 import SpotifyOAuth
from cacher import load_access_token
import six.moves.urllib.parse as urllibparse

client_id_and_secret = None

scope = 'playlist-read-private, user-read-private'


def read_client_id_and_secret():
    global client_id_and_secret
    with open('secret//secrets.json', 'r') as secret_file:
        client_id_and_secret = json.load(secret_file)
    if client_id_and_secret is None:
        raise Exception("can't obtain client id and client secret")


def get_client_id():
    if client_id_and_secret is None:
        read_client_id_and_secret()
    return client_id_and_secret['id']


def get_client_secret():
    if client_id_and_secret is None:
        read_client_id_and_secret()
    return client_id_and_secret['secret']


def get_redirect_uri():
    if client_id_and_secret is None:
        read_client_id_and_secret()
    return client_id_and_secret['redirect_uri']


class userDataProvider:
    def __init__(self, access_token):
        try:
            self.user_data = requester.get_me(access_token)
            self.success = True
        except:
            self.success = False

    def is_successful(self):
        return self.success

    def get_username(self):
        split_user_data = self.user_data['uri'].split(':')
        username = split_user_data[2] if len(split_user_data) > 1 else None

        if username is None:
            print('cannot get username')
        return username

    def get_display_name(self):
        if 'display_name' not in self.user_data.keys():
            return None
        return self.user_data['display_name']


def try_load_access_token(username):
    if username is not None:
        access_token = load_access_token(username)
        if access_token is not None:
            return access_token, userDataProvider(access_token)
    return None


def get_access_token(url_taker, auth_giver):
    sp_oauth = SpotifyOAuth(client_id=get_client_id(),
                            client_secret=get_client_secret(),
                            redirect_uri=get_redirect_uri(),
                            scope=scope,
                            cache_path='secret\\'
                            )

    print('''

        User authentication requires interaction with your
        web browser. Once you enter your credentials and
        give authorization, you will be redirected to
        a url.  Paste that url you were directed to to
        complete the authorization.

    ''')

    auth_url = sp_oauth.get_authorize_url()

    url_taker.take(auth_url)

    print()
    print()

    response = auth_giver.give()

    print()
    print()

    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        print("can't get token")
    else:
        print(token_info['access_token'])
        print(token_info['expires_in'])

    token = token_info['access_token']
    user_data_provider = userDataProvider(token)

    return token, user_data_provider, token_info['expires_in']
