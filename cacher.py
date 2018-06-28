import os
import datetime
import json


def dump_access_token(username, token, expires_in):
    if not os.path.exists('secret'):
        os.makedirs('secret')

    tokens_file_name = 'secret\\tokens.json'
    with open(tokens_file_name, 'w') as file:
        json.dump({username: token, 'expires_in': expires_in, 'acquired_at': str(datetime.datetime.now())}, file)

def load_access_token(username):
    tokens_file_name = 'secret\\tokens.json'
    if os.path.isfile(tokens_file_name):
        with open(tokens_file_name, 'r') as file:
            data = json.load(file)
            if data is not None:
                acquired_at = datetime.datetime.strptime(data['acquired_at'], '%Y-%m-%d %H:%M:%S.%f')
                time_elapsed = datetime.datetime.now() - acquired_at
                if time_elapsed.total_seconds() < data['expires_in']:
                    return data[username]
    return None

def dump_data(spotify_data_type, spotify_data_id, username, data):
    user_id = username
    if not os.path.exists('collected_data'):
        os.makedirs('collected_data')
    user_path = 'collected_data\\{user_id}'.format(user_id=user_id)
    user_file_name = 'collected_data\\users.json'
    users_data = dict()
    if os.path.isfile(user_file_name):
        with open(user_file_name, 'r') as user_file:
            users_data = json.load(user_file)
    users_data[user_id] = datetime.datetime.now().strftime('%y-%m-%d %H:%M')
    location = user_path + '\\{type}'.format(type=spotify_data_type)
    obs_name = user_path + '\\{type}.json'.format(type=spotify_data_type)
    obser_data = dict()
    if os.path.isfile(obs_name):
        with open(obs_name, 'r') as observer:
            obser_data = json.load(observer)
    obser_data[spotify_data_id] = datetime.datetime.now().strftime('%y-%m-%d %H:%M')
    if not os.path.exists(location):
        os.makedirs(location)
    dump_file_name = location + '\\{data_id}.json'.format(data_id=spotify_data_id)
    with open(dump_file_name, 'w') as outfile:
        json.dump(data, outfile)
    with open(obs_name, 'w') as observer:
        json.dump(obser_data, observer)
    with open(user_file_name, 'w') as user_file:
        json.dump(users_data, user_file, separators=('\n', ':'))

def load_data(spotify_data_type, spotify_data_id, username):
    user_id = username
    user_file_name = 'collected_data\\users.json'
    if os.path.isfile(user_file_name):
        with open(user_file_name, 'r') as user_file:
            users_data = json.load(user_file)
            if user_id in users_data.keys():
                user_path = 'collected_data\\{user_id}'.format(user_id=user_id)
                data_path = user_path + '\\{data_type}'.format(data_type=spotify_data_type)
                data_file_name = user_path + '\\{data_type}.json'.format(data_type=spotify_data_type)
                with open(data_file_name) as data_file:
                    obs_data = json.load(data_file)
                    if spotify_data_id in obs_data.keys():
                        final_data_name = data_path + '\\{0}.json'.format(spotify_data_id)
                        with open(final_data_name, 'r') as final_data_file:
                            res = json.load(final_data_file)
                            return res
    return None
