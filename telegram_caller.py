import sys
import telepot
import time
import json
import threading
import export_playlist

chat_to_spotify_ids_dict = dict()
bot_id, stop_word = None, None
with open('secret//bot_secret.json', 'r') as file:
    data = json.load(file)
    bot_id = data['bot_id']
    stop_word = data['stop_word']


class ExportSessionState:
    Init, Login, WaitToken, CollectPlaylists, SelectPlaylist, CollectTracks, Continue, Done = range(8)


class TelegramListener:
    def __init__(self, t_bot, chat_id, telegram_user_id):
        self.bot = t_bot
        self.chat_id = chat_id
        self.t_user_id = telegram_user_id
        if self.chat_id in chat_to_spotify_ids_dict.keys():
            self.s_user_id = chat_to_spotify_ids_dict[self.chat_id]
        else:
            self.s_user_id = None
        self.current_platform = "Spotify"
        self.waiting_for_token = False
        self.auth_response = None
        self.exporter = None
        self.state = ExportSessionState.Init
        print('listerner: basic init finished')

    def _wait_for_token(self):
        while self.waiting_for_token:
            time.sleep(1)

    def go_to_next_state(self):
        if self.state == ExportSessionState.WaitToken:
            self.state = ExportSessionState.CollectPlaylists
            self.show_playlists()

    def acquire_access_token(self):
        self.state = ExportSessionState.Login
        self.exporter = export_playlist.playlistExporter(self.s_user_id, self, self)
        self.s_user_id = self.exporter.get_username()
        print('telegram listener initialized. user={0}, spotify_id={1}'.format(self.t_user_id, self.s_user_id))
        chat_to_spotify_ids_dict[self.chat_id] = self.s_user_id
        self.go_to_next_state()

    def take(self, auth_url):
        log_in_msg = "Please, follow the link bellow to login into {p}.\n{url}" \
                     .format(p=self.current_platform, url=auth_url)
        self.bot.sendMessage(self.chat_id, log_in_msg)
        self.state = ExportSessionState.WaitToken

    def give(self):
        self.waiting_for_token = True
        msg = "After you've logged in you will be redirected." \
              "Send that link where you ended up here."
        self.bot.sendMessage(self.chat_id, msg)
        self._wait_for_token()
        print('finished waiting...', self.auth_response)
        return self.auth_response

    def hears(self, message):
        print('listener: hear {0}'.format(message))
        if self.waiting_for_token:
            self.auth_response = message
            self.waiting_for_token = False
        elif self.state == ExportSessionState.SelectPlaylist:
            number_of_playlists = len(self.exporter.playlists)
            try:
                selected_playlist = int(message)
                if selected_playlist >= number_of_playlists:
                    raise ValueError("Selected playlist number is out of range")
            except:
                self.bot.sendMessage(self.chat_id, "Yeah, I need a number (<{0})".format(number_of_playlists))
            self.give_the_playlist(selected_playlist)
        elif self.state == ExportSessionState.Continue:
            if message == '/no':
                self.state = ExportSessionState.Done
            elif message == '/yes':
                self.state = ExportSessionState.SelectPlaylist
            else:
                self.state = ExportSessionState.SelectPlaylist
                self.hears(message)

    def give_the_playlist(self, number):
        self.state = ExportSessionState.CollectTracks
        file_directory = self.exporter.get_export_file(number)
        with open(file_directory, 'r') as file:
            self.bot.sendDocument(self.chat_id, file)
        self.state = ExportSessionState.Continue
        self.bot.sendMessage(self.chat_id, "Export another playlist? (/yes /no or number)")

    def show_playlists(self):
        msg = "Select a playlist to export:\n" + \
               '\n'.join([str(i+1) + ' ' + p for i, p in enumerate(self.exporter.get_praylists())])
        self.bot.sendMessage(self.chat_id, msg)
        self.state = ExportSessionState.SelectPlaylist

    def is_finished(self):
        return self.state == ExportSessionState.Done


listener = None
t_init_listener = threading.Thread(target=None)
t_init_flag = False
wait_for_init_start = True
lock = threading.Lock()

def handle(message):
    global listener, t_init_listener, t_init_flag, complete_stop, lock, main_breaker, wait_for_init_start
    chat_id = message['chat']['id']

    t_username = None
    if 'from' in message:
        if 'username' in message['from']:
            t_username = message['from']['username']

    bot.sendMessage(chat_id, message['text'])
    command = message['text']
    if listener is None or command == '/start':
        with lock:
            print("handle: locked")
            t_init_listener = threading.Thread(target=None)
            t_init_flag = False
            wait_for_init_start = True
            main_breaker = True
            time.sleep(3)
            listener = TelegramListener(bot, chat_id, t_username)
            t_init_listener = threading.Thread(target=listener.acquire_access_token)
            t_init_flag = True

    elif command == stop_word:
        complete_stop = True

    listener.hears(command)


bot = telepot.Bot(bot_id)
bot.message_loop(handle)


print 'I am listening ...'
complete_stop = False
main_breaker = False

def refresh_listener():
    global listener
    if listener is not None:
        if listener.is_finished():
            listener = None
            print("refresh!!!")


class Looper:
    def __init__(self):
        self.main_runs = True
        self.loop_main()

    def loop_init(self):
        global main_breaker, wait_for_init_start
        while not self.main_runs:
            if t_init_flag:
                t_init_listener.start()
                wait_for_init_start = False
                t_init_listener.join()
                main_breaker = False
                print("init loop: init listener joined")

            if not main_breaker:
                break
        self.main_runs = True
        self.loop_main()

    def loop_main(self):
        while self.main_runs:
            print("main loop:")
            refresh_listener()
            if main_breaker or complete_stop:
                break
            time.sleep(1)
        self.main_runs = False
        if not complete_stop:
            self.loop_init()


t_main_loop = threading.Thread(target=Looper)
t_main_loop.start()
t_main_loop.join()
