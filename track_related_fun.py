
def get_data_for_track(track_id):
    data = load_data('tracks_features', track_id, my_user_id)
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
        dump_data('tracks_features', track_id, my_user_id, data)
    return data


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
