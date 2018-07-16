import threading
import time
import export_playlist
import cacher


class PlaylistExportState(object):
    def __init__(self, t_bot, chat_id, exporter=None):
        self.bot = t_bot
        self.chat_id = chat_id
        self.current_platform = "Spotify"
        self.exporter = exporter

    def _send_msg(self, message, disable_preview = False):
        self.bot.sendMessage(self.chat_id, message, disable_web_page_preview=disable_preview)

    def change_state(self, communicator, state):
        communicator._change_state(state)

    def login_start(self, communicator):
        pass

    def login_finish(self, communicator):
        pass

    def show_playlists(self, communicator):
        pass

    def all(self, communicator):
        pass

    def hear(self, communicator, word):
        print('hear {} and do nothing'.format(word))
        pass


class LoginState(PlaylistExportState):
    def __init__(self, bot, chat_id):
        super(LoginState, self).__init__(bot, chat_id)
        self.acquire_thread = threading.Thread(target=None)
        self.authorized = False
        self.auth_response = None
        self._send_msg('Use /start')

    def _acquire_access_token(self):
        user = cacher.load_last_acquired_user()

        # tmp
        user = None
        #

        self.exporter = export_playlist.playlistExporter(user, self, self)
        self.spotify_user_id = self.exporter.get_username()
        if self.exporter.is_successful():
            print('authorized successfully')
            self.authorized = True

    def login_start(self, communicator):
        self.acquire_thread = threading.Thread(target=self._acquire_access_token)
        self.acquire_thread.start()

    def login_finish(self, communicator):
        self.acquire_thread.join()
        next_state = SelectPlaylistState(self.bot, self.chat_id, self.exporter)
        super(LoginState, self).change_state(communicator, next_state)

    def hear(self, communicator, word):
        if word[0:4] == 'http':
            self.auth_response = word
            while not self.authorized:
                time.sleep(1)
            self.login_finish(communicator)

    def take(self, auth_url):
        self._send_msg('Log in into {0} using the link below \n{1}\n'
                       "After you logged in, copy the link you're redirected to"
                        .format(self.current_platform, auth_url),
                       disable_preview=True)

    def give(self):
        while self.auth_response is None:
            time.sleep(1)
        print('token received. chat:{0}'.format(self.chat_id))
        return self.auth_response


class SelectPlaylistState(PlaylistExportState):
    def __init__(self, bot, chat_id, exporter):
        super(SelectPlaylistState, self).__init__(bot, chat_id, exporter)
        self._send_msg('Use /show_playlists to see your playlist on {}'.format(self.current_platform))

    def show_playlists(self, communicator):
        msg = "Select a playlist to export:\n" + \
               '\n'.join([str(i+1) + ' ' + p for i, p in enumerate(self.exporter.get_playlists_names())])
        self._send_msg(msg)
        next_state = ExportingState(self.bot, self.chat_id, self.exporter)
        super().change_state(communicator, next_state)


class ExportingState(PlaylistExportState):
    def __init__(self, bot, chat_id, exporter):
        super().__init__(bot, chat_id, exporter)
        self._send_msg('Use number or /all')

    def _give_playlist(self, number):
        file_directory = self.exporter.get_export_file(number)
        with open(file_directory, 'r') as file:
            print("give the playlist: about to send file:", file_directory)
            try:
                what = self.bot.sendDocument(self.chat_id, file)
            except Exception as e:
                print(e.message)

    def hear(self, communicator, word):
        try:
            number_of_playlists = len(self.exporter.get_playlists())
            selected_playlist = int(word)
            if selected_playlist >= number_of_playlists:
                raise ValueError("Selected playlist number is out of range")
            self._give_playlist(selected_playlist)
            next_state = ContinueState(self.bot, self.chat_id, self.exporter)
            super().change_state(communicator, next_state)
        except ValueError:
            pass

    def all(self, communicator):
        playlists_count = len(self.exporter.get_playlists())
        if playlists_count == 0:
            self._send_msg("It seems that you've got no playlists on {}".format(self.current_platform))
        else:
            for number in range(playlists_count):
                self._give_playlist(number)

        next_state = ContinueState(self.bot, self.chat_id, self.exporter)
        super().change_state(communicator, next_state)


class ContinueState(PlaylistExportState):
    def __init__(self, bot, chat_id, exporter):
        super().__init__(bot, chat_id, exporter)
        print("Entered ContinueState")
