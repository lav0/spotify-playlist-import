import os

def write_as_csv(playlist_name, tracks):
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_dir + '\\' + playlist_name + '.csv', 'w') as export_file:
        template_str = "{0}, {1}, {2}, {3}\n"
        export_file.write(template_str.format('title', 'artist', 'album', 'featuring artists'))
        for track in tracks:
            main_artist = track['artists'][0]['name']
            main_artist = "".join(main_artist.split(","))
            track_name = track['name']
            track_name = "".join(track_name.split(","))
            album_name = track['album']['name']
            album_name = "".join(album_name.split(","))
            featuring_artists = ''
            if len(track['artists']) > 1:
                featuring_artists = '-'.join([t['name'] for t in track['artists'][1:]])
            full_entry = template_str.format(track_name.encode('utf8'),
                                             main_artist.encode('utf8'),
                                             album_name.encode('utf8'),
                                             featuring_artists.encode('utf8'))
            export_file.write(full_entry)
