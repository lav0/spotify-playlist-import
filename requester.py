import requests
import json
from cacher import dump_data, load_data


class SpotifyCaller:
    def __init__(self, username, access_token):
        self.username = username
        self.access_token = access_token
        self.only_self_made = True
        self.playlists = list()

    def get_playlist_name(self, playlist_number):
        if playlist_number > len(self.playlists):
            del self.playlists[:]
            self.get_playlists()
        if playlist_number > len(self.playlists):
            return None
        return self.playlists[playlist_number - 1]['name']

    def get_playlist_tracks(self, playlist_number):
        user_id = self.username
        if playlist_number > len(self.playlists):
            del self.playlists[:]
            self.get_playlists()
        if playlist_number > len(self.playlists):
            return None
        playlist_id = self.playlists[playlist_number - 1]['id']
        session = requests.Session()
        method = 'GET'
        url = 'https://api.spotify.com/v1/users/{user_id}/playlists/{playlist_id}/tracks'
        url = url.format(user_id=user_id, playlist_id=playlist_id)
        url += '/?limit={limit}&offset={offset}'
        headers = {'Accept': 'application/json'}
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer {0}'.format(self.access_token)
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

    def get_playlists(self):
        user_id = self.username
        session = requests.Session()
        url = 'https://api.spotify.com/v1/users/{user_id}/playlists'
        url = url.format(user_id=user_id)
        url += '?limit={limit}&offset={offset}'
        headers = {'Accept': 'application/json'}
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer {0}'.format(self.access_token)
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
        if self.only_self_made:
            items = [x for x in items if x['owner']['id'] == user_id]
        self.playlists = items
        return items
