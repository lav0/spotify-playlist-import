import json
import io
from random import randint
from requester import get_data_for_track
from requester import get_playlist_tracks
from requester import get_playlist_for_user

def show_playlists():
    with open('get-playlist-sample.json') as f:
        data = json.load(f)
        items = data['items']
        for item in items:
            print(item['name'], item['id'])

def show_tracks_by_criterio(tracks, criterio='popularity'):
    if criterio is not 'popularity':
        print('trying to retrieve additional features')
        for track in tracks:
            try:
                track_id = track['id']
                if track_id is None:
                    raise
                new_data = get_data_for_track(track_id)
                track[criterio] = new_data[criterio]
            except:
                track[criterio] = None
                print('cannot read additional features', track['name'])
    by_popularity = sorted(tracks, key=lambda x: x[criterio])
    for track, i in zip(by_popularity, range(len(tracks))):
        print(i, criterio,'=', [track[criterio], track['artists'][0]['name'], track['name']])

# tracks0 = get_playlist_tracks('1az1W6sKHKiJtLblArkk6r')
# tracks1 = get_playlist_tracks('73ug8UQPmKJr2E06tx3cD0')
# tracks2 = get_playlist_tracks('4trN07FhyPhZTEKdWxg9wH')
#
# show_tracks_by_criterio(tracks0 + tracks1 + tracks2, 'danceability')

playlists = get_playlist_for_user(only_self_made=True)[0:1]

all_tracks_in_my_playlists = []
for pl in playlists:
    tracks_for_currect = get_playlist_tracks(pl['id'])
    all_tracks_in_my_playlists += tracks_for_currect
    print('tracks received for',(pl['name']), len(tracks_for_currect))
show_tracks_by_criterio(all_tracks_in_my_playlists, 'valence')
