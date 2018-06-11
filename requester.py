import requests
import json
import os
import datetime

auth = 'BQCtFqz_ItmW_POPDJatMnjkwGlcCuBxGKM9jBuKX3tmBbTHwe2jg_NTf2NMRTZxOuI1213NcgcLRqOQOQK_o7jHIU1_sxsoXQTlg6EwY8hzytQ-ycIHwiGg_7-70nUMrnlLfyCoAuOLod3U4LISqRxGQxtkw1TgfABSZiWL_2GLCIbwo-Y'
my_user_id = '214uc47fxa56xsnfn6aguxxry'

def dump_data(spotify_data_type, spotify_data_id, data):
    global my_user_id
    user_id = my_user_id
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

def load_data(spotify_data_type, spotify_data_id):
    global my_user_id
    user_id = my_user_id
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

def get_data_for_track(track_id):
    data = load_data('tracks_features', track_id)
    if data is None:
        session = requests.Session()
        method = 'GET'
        url = 'https://api.spotify.com/v1/audio-features/{0}'.format(track_id)
        headers = {'Accept': 'application/json'}
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer {0}'.format(auth)
        r = session.request(method, url, headers=headers)
        data = r.json()
        if 'error' in data.keys():
            print('error', data['error'])
        dump_data('tracks_features', track_id, data)
    else:
        print('used written data')
    return data

def get_playlist_tracks(playlist_id):
    global my_user_id
    user_id = my_user_id
    session = requests.Session()
    method = 'GET'
    url = 'https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}/tracks'
    url = url.format(user_id=user_id, playlist_id=playlist_id)
    url += '/?limit={limit}&offset={offset}'
    headers = {'Accept': 'application/json'}
    headers['Content-Type'] = 'application/json'
    headers['Authorization'] = 'Bearer {0}'.format(auth)
    lim = 25
    off = 0
    carry_on = True
    items = list()
    while carry_on:
        r = session.request(method, url.format(limit=lim, offset=off), headers=headers)
        low_data = r.json()
        new_items = low_data['items']
        items += new_items
        carry_on = len(new_items) == lim
        off += lim
    tracks = list()
    for item in items:
        tracks.append(item['track'])
    return tracks

def get_playlist_for_user(user_id=my_user_id, only_self_made=False):
    session = requests.Session()
    url = 'https://api.spotify.com/v1/users/{user_id}/playlists'
    url = url.format(user_id=user_id)
    url += '?limit={limit}&offset={offset}'
    headers = {'Accept': 'application/json'}
    headers['Content-Type'] = 'application/json'
    headers['Authorization'] = 'Bearer {0}'.format(auth)
    lim = 30
    off = 0
    carry_on = True
    items = list()
    while carry_on:
        r = session.request('GET', url.format(limit=lim, offset=off), headers=headers)
        low_data = r.json()
        new_items = low_data['items']
        items += new_items
        carry_on = len(new_items) == lim
        off += lim
    if only_self_made:
        items = [x for x in items if x['owner']['id'] == user_id]
    return items
