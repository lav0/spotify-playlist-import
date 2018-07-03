import sys
import io
import telepot
import time
import json
import threading
import export_playlist
import cacher # tmp


activeListeners = dict()

bot_id, stop_word = None, None
with open('secret//bot_secret.json', 'r') as file:
    data = json.load(file)
    bot_id = data['bot_id']
    stop_word = data['stop_word']

commands = ['/login', '/start', '/show_playlists', '/all', '/yes', '/no' '/finish']


class ExportSessionState:
    Init, Login, SelectPlaylist, Continue, Done = range(5)

class TelegramListener:
    def __init__(self, t_bot, chat_id):
        self.bot = t_bot
        self.chat_id = chat_id
        self.spotify_user_id = None
        self.current_platform = "Spotify"
        self.auth_response = None
        self.exporter = None
        self.state = ExportSessionState.Init
        self.acquire_thread = threading.Thread(target=None)
        print('listerner: basic init finished. chat:{0}'.format(chat_id))

    def _acquire_access_token(self):
        user = cacher.load_last_acquired_user()
        self.exporter = export_playlist.playlistExporter(user, self, self)
        self.spotify_user_id = self.exporter.get_username()
        if self.exporter.is_successful():
            print('authorized successfully')
            self.state = ExportSessionState.SelectPlaylist

    def _send_msg(self, message, disable_preview = False):
        # with threading.Lock():
        self.bot.sendMessage(self.chat_id, message, disable_web_page_preview=disable_preview)

    def _log_in(self):
        self.state = ExportSessionState.Login
        self.acquire_thread = threading.Thread(target=self._acquire_access_token)
        self.acquire_thread.start()

    def take(self, auth_url):
        self._send_msg('Log in into {0} using the link below \n{1}\n' \
                       "After you logged in, copy the link you're redirected to"
                        .format(self.current_platform, auth_url), True)

    def give(self):
        while self.state == ExportSessionState.Login:
            time.sleep(1)
        print('token received. chat:{0}'.format(self.chat_id))
        return self.auth_response

    def show_playlists(self):
        self.acquire_thread.join()
        msg = "Select a playlist to export (number or /all) :\n" + \
               '\n'.join([str(i+1) + ' ' + p for i, p in enumerate(self.exporter.get_playlists_names())])
        self.bot.sendMessage(self.chat_id, msg)

    def give_the_playlist(self, number):
        file_directory = self.exporter.get_export_file(number)
        # under develompent
        with io.open("unicode_inside.txt", 'r', encoding='utf8') as file:
            print("give the playlist: about to send file:", file_directory)
            try:
                what = self.bot.sendDocument(self.chat_id, file)
            except Exception as e:
                print(e.message)


    def hear_command(self, command):
        if command == '/login' or command == '/start':
            self._log_in()
        elif command == '/show_playlists':
            if self.state == ExportSessionState.SelectPlaylist:
                self.show_playlists()
        elif command == '/all':
            if self.state == ExportSessionState.SelectPlaylist:
                for number in range(len(self.exporter.get_playlists())):
                    self.give_the_playlist(number)
        elif command == '/yes':
            if self.state == ExportSessionState.Continue:
                self.state = ExportSessionState.SelectPlaylist
                self.show_playlists()
        elif command == '/finish' or command == '/no':
            pass
        else:
            print('unknown command: ', command)

    def hear_word(self, word):
        if word[0:4] == 'http':
            self.auth_response = word
        else:
            try:
                number_of_playlists = len(self.exporter.get_playlists())
                selected_playlist = int(word)
                if selected_playlist >= number_of_playlists:
                    raise ValueError("Selected playlist number is out of range")
                self.give_the_playlist(selected_playlist)
                self.state = ExportSessionState.Continue
                self._send_msg("Export another playlist? (/yes /all /no or number)")
            except ValueError:
                pass


def handle(message):
    global complete_stop
    if message['text'] == stop_word:
        complete_stop = True

    chat_id = message['chat']['id']
    if chat_id not in activeListeners.keys():
        activeListeners[chat_id] = TelegramListener(bot, chat_id)

    command = message['text']
    if command in commands:
        activeListeners[chat_id].hear_command(command)
    else:
        activeListeners[chat_id].hear_word(command)

    bot.sendMessage(chat_id, command)

bot = telepot.Bot(bot_id)
bot.message_loop(handle)
print 'I am listening ...'
with io.open("unicode_inside.txt", 'r', encoding='utf8') as file:
    print("about to send the file")
    what = bot.sendDocument(70943200, file)

complete_stop = False
while True:
    for chat_id in activeListeners.keys():
        print("chat: {0}, state: {1}".format(chat_id, str(activeListeners[chat_id].state)))
    if complete_stop:
        break
    time.sleep(1)
