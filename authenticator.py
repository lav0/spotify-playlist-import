import requests
import json
from oauth2 import SpotifyOAuth
from cacher import load_access_token, dump_access_token
import six.moves.urllib.parse as urllibparse

client_id_and_secret = None
my_user_id = '214uc47fxa56xsnfn6aguxxry'

scope = 'playlist-read-private'

def read_client_id_and_secret():
    global client_id_and_secret
    with open('secret\\secrets.json', 'r') as secret_file:
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

def get_access_token():
    sp_oauth = SpotifyOAuth(client_id=get_client_id(),
                            client_secret=get_client_secret(),
                            redirect_uri=get_redirect_uri(),
                            scope=scope,
                            cache_path='secret\\')

    access_token = load_access_token(my_user_id)
    if access_token is not None:
        return access_token

    print('''

        User authentication requires interaction with your
        web browser. Once you enter your credentials and
        give authorization, you will be redirected to
        a url.  Paste that url you were directed to to
        complete the authorization.

    ''')

    auth_url = sp_oauth.get_authorize_url()

    try:
        import webbrowser
        webbrowser.open(auth_url)
        print("Opened %s in your browser" % auth_url)
    except:
        print("Please navigate here: %s" % auth_url)

    print()
    print()

    try:
        response = raw_input("Enter the URL you were redirected to: ")
    except NameError:
        response = input("Enter the URL you were redirected to: ")

    print()
    print()

    code = sp_oauth.parse_response_code(response)
    token_info = sp_oauth.get_access_token(code)

    if not token_info:
        print "can't get token"
    else:
        print(token_info['access_token'])
        print(token_info['expires_in'])

    dump_access_token(username=my_user_id, token=token_info['access_token'], expires_in=token_info['expires_in'])

    return token_info['access_token']
