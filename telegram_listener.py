import export_playlist
from playlist_export_state import LoginState

class TelegramListener:
    def __init__(self, t_bot, chat_id):
        self.state = LoginState(t_bot, chat_id)
        # self.spotify_user_id = None
        # self.current_platform = "Spotify"
        # self.auth_response = None
        # self.exporter = None
        # self.state = ExportSessionState.Init
        # self.acquire_thread = threading.Thread(target=None)
        print('listerner: basic init finished. chat:{0}'.format(chat_id))

    def _change_state(self, state):
        self.state = state

    def _send_msg(self, message, disable_preview = False):
        self.bot.sendMessage(self.chat_id, message, disable_web_page_preview=disable_preview)

    def is_authorized(self):
        return self.state.is_authorized(self)

    def login_start(self):
        self.state.login_start(self)

    def login_finish(self):
        self.state.login_finish(self)

    def hear_word(self, word):
        self.state.hear(self, word)

    def show_playlists(self):
        self.state.show_playlists(self)

    def all(self):
        self.state.all(self)
