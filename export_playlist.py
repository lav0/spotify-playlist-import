import json
import io
import playlist_writer
from random import randint
import authenticator
from requester import SpotifyCaller


class authUrlTaker:
    def take(self, auth_url):
        try:
            import webbrowser
            webbrowser.open(auth_url)
            print("Opened %s in your browser" % auth_url)
        except:
            print("Please navigate here: %s" % auth_url)


class authTokenGiver():
    def give(self):
        try:
            response = raw_input("Enter the URL you were redirected to: ")
        except NameError:
            response = input("Enter the URL you were redirected to: ")
        return response


class PlaylistExporter:
    def __init__(self,
                 token=None,
                 name_provider=None,
                 auth_url_taker=authUrlTaker(),
                 auth_token_giver=authTokenGiver()):
        if token is None or name_provider is None:
            token, name_provider = authenticator.get_access_token(auth_url_taker, auth_token_giver)
            self.access_token = token
            self.name_provider = name_provider
        else:
            self.access_token = token
            self.name_provider = name_provider
        self.spotify_caller = SpotifyCaller(self.get_username(), self.access_token)
        self.playlists = []

    def is_successful(self):
        return self.name_provider.is_successful()

    def get_username(self):
        return self.name_provider.get_username()

    def get_display_name(self):
        disp_name = self.name_provider.get_display_name()
        return self.get_username() if disp_name is None else disp_name

    def get_playlists(self):
        if len(self.playlists) == 0:
            self.playlists = self.spotify_caller.get_playlists()
        return self.playlists

    def get_playlists_names(self):
        return [p['name'] for p in self.get_playlists()]

    def get_export_file(self, playlist_number_to_export):
        playlist_name = self.spotify_caller.get_playlist_name(playlist_number_to_export)
        if playlist_name is not None:
            tracks = self.spotify_caller.get_playlist_tracks(playlist_number_to_export)
            exported_file = playlist_writer.write_as_csv(self.get_display_name(), playlist_name, tracks)
            return exported_file
        else:
            print('playlist is not found')

        # for playlist in playlists:
        #     dump_data(spotify_data_type='playlists', spotify_data_id=playlist['id'], username=my_user_id, data=playlist)

        return None
