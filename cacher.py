import os
import datetime
import json


def get_tokens_file_name():
    return 'secret/tokens.json'


def dump_access_token(chat_id, username, token, expires_in):
    if not os.path.exists('secret'):
        os.makedirs('secret')

    tokens_file_name = get_tokens_file_name()
    if not os.path.isfile(tokens_file_name):
        file = open(tokens_file_name, 'w')
        file.close()
    with open(tokens_file_name, 'r+') as file:
        try:
            data = json.load(file)
        except ValueError:
            data = dict()
        new_entry = {'username': username, 'token': token, 'expires_in': expires_in, 'acquired_at': str(datetime.datetime.now())}
        data[chat_id] = new_entry
        json.dump(data, file, indent=2)


def load_access_token(username):
    tokens_file_name = get_tokens_file_name()
    if os.path.isfile(tokens_file_name):
        with open(tokens_file_name, 'r') as file:
            data = json.load(file)
            if data is not None:
                for entry in data:
                    if entry['username'] == username:
                        acquired_at = datetime.datetime.strptime(entry['acquired_at'], '%Y-%m-%d %H:%M:%S.%f')
                        time_elapsed = datetime.datetime.now() - acquired_at
                        if time_elapsed.total_seconds() < entry['expires_in']:
                            return entry['token']
    return None


def load_last_acquired_user():
    tokens_file_name = get_tokens_file_name()
    if os.path.isfile(tokens_file_name):
        with open(tokens_file_name, 'r') as file:
            data = json.load(file)
            if data is not None:
                last_acquired_time = datetime.datetime(year=2018, month=1, day=1)
                last_acquired_user = None
                for entry in data:
                    acquired_at = datetime.datetime.strptime(entry['acquired_at'], '%Y-%m-%d %H:%M:%S.%f')
                    if last_acquired_time < acquired_at:
                        last_acquired_time = acquired_at
                        last_acquired_user = entry['username']
                return last_acquired_user
    return None


def dump_data(spotify_data_type, spotify_data_id, username, data):
    user_id = username
    if not os.path.exists('collected_data'):
        os.makedirs('collected_data')
    user_path = 'collected_data//{user_id}'.format(user_id=user_id)
    user_file_name = 'collected_data//users.json'
    users_data = dict()
    if os.path.isfile(user_file_name):
        with open(user_file_name, 'r') as user_file:
            users_data = json.load(user_file)
    users_data[user_id] = datetime.datetime.now().strftime('%y-%m-%d %H:%M')
    location = user_path + '//{type}'.format(type=spotify_data_type)
    obs_name = user_path + '//{type}.json'.format(type=spotify_data_type)
    obser_data = dict()
    if os.path.isfile(obs_name):
        with open(obs_name, 'r') as observer:
            obser_data = json.load(observer)
    obser_data[spotify_data_id] = datetime.datetime.now().strftime('%y-%m-%d %H:%M')
    if not os.path.exists(location):
        os.makedirs(location)
    dump_file_name = location + '//{data_id}.json'.format(data_id=spotify_data_id)
    with open(dump_file_name, 'w') as outfile:
        json.dump(data, outfile)
    with open(obs_name, 'w') as observer:
        json.dump(obser_data, observer)
    with open(user_file_name, 'w') as user_file:
        json.dump(users_data, user_file, separators=('\n', ':'))


def load_data(spotify_data_type, spotify_data_id, username):
    user_id = username
    user_file_name = 'collected_data//users.json'
    if os.path.isfile(user_file_name):
        with open(user_file_name, 'r') as user_file:
            users_data = json.load(user_file)
            if user_id in users_data.keys():
                user_path = 'collected_data//{user_id}'.format(user_id=user_id)
                data_path = user_path + '//{data_type}'.format(data_type=spotify_data_type)
                data_file_name = user_path + '//{data_type}.json'.format(data_type=spotify_data_type)
                with open(data_file_name) as data_file:
                    obs_data = json.load(data_file)
                    if spotify_data_id in obs_data.keys():
                        final_data_name = data_path + '//{0}.json'.format(spotify_data_id)
                        with open(final_data_name, 'r') as final_data_file:
                            res = json.load(final_data_file)
                            return res
    return None
