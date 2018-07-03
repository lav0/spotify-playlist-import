import os
import io

def write_as_csv(username, playlist_name, tracks):
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir_user = output_dir + '\\' + username
    if not os.path.exists(output_dir_user):
        os.makedirs(output_dir_user)
    file_name = output_dir_user + '\\' + playlist_name + '.csv'
    with open(file_name, 'w') as export_file:
        template_str = u'{0}, {1}, {2}, {3}\n'
        export_file.write(template_str.format(u'title', u'artist', u'album', u'featuring artists'))
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
        return file_name
    return None
