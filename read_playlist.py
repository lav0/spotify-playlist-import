import json
import io
import playlist_writer
from random import randint
import authenticator
from requester import SpotifyCaller
from cacher import dump_data


# my_user_id = '214uc47fxa56xsnfn6aguxxry'

def export_praylists():
    access_token, username = authenticator.get_access_token()

    caller = SpotifyCaller(username, access_token)
    playlists = caller.get_playlists()

    print('the playlists:')
    for playlist, number in zip(playlists, range(len(playlists))):
        print(number+1, playlist['name'], playlist['id'])

    playlist_number_to_export = 0
    while playlist_number_to_export == 0:
        playlist_number_to_export = int(raw_input("Enter the number of playlist to export: "))

    playlist_name = caller.get_playlist_name(playlist_number_to_export)
    if playlist_name is not None:
        exported_file = playlist_writer.write_as_csv(playlist_name, caller.get_playlist_tracks(playlist_number_to_export))
        return exported_file
    else:
        print('playlist is not found')

    # for playlist in playlists:
    #     dump_data(spotify_data_type='playlists', spotify_data_id=playlist['id'], username=my_user_id, data=playlist)

    return None


print export_praylists()
