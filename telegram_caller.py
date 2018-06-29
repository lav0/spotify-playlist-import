import sys
import telepot
import time
import json
import threading
import export_playlist

telegram_to_spotify_user_id = dict()
bot_id, stop_word = None, None
with open('secret//bot_secret.json', 'r') as file:
    data = json.load(file)
    bot_id = data['bot_id']
    stop_word = data['stop_word']


class TelegramListener:
    def __init__(self, t_bot, chat_id, telegram_user_id):
        self.bot = t_bot
        self.chat_id = chat_id
        self.t_user_id = telegram_user_id
        if self.t_user_id in telegram_to_spotify_user_id.keys():
            self.s_user_id = telegram_to_spotify_user_id[self.t_user_id]
        else:
            self.s_user_id = None
        self.current_platform = "Spotify"
        self.waiting_for_token = False
        self.auth_response = None
        self.exporter = None
        print('listerner: basic init finished')

    def _wait_for_token(self):
        while self.waiting_for_token:
            time.sleep(1)

    def acquire_access_token(self):
        print('listerner: token init started')
        self.exporter = export_playlist.playlistExporter(self.s_user_id, self, self)
        self.s_user_id = self.exporter.get_username()
        print('telegram listener initialized. user={0}, spotify_id={1}'.format(self.t_user_id, self.s_user_id))
        telegram_to_spotify_user_id[self.t_user_id] = self.s_user_id
        self.show_playlists()

    def take(self, auth_url):
        log_in_msg = "Please, follow the link bellow to login into {p}:\n {url}".format(p=self.current_platform, url=auth_url)
        self.bot.sendMessage(self.chat_id, log_in_msg)

    def give(self):
        self.waiting_for_token = True
        msg = "Please, copy the link you've been redircted to and send it here"
        self.bot.sendMessage(self.chat_id, msg)
        self._wait_for_token()
        print('finished waiting...', self.auth_response)
        return self.auth_response

    def hears(self, message):
        print('listener: hear {0}'.format(message))
        if self.waiting_for_token:
            self.auth_response = message
            self.waiting_for_token = False

    def show_playlists(self):
        msg = '\n'.join([str(i+1) + ' ' + p for i, p in enumerate(self.exporter.get_praylists())])
        self.bot.sendMessage(self.chat_id, msg)


listener = None
t_init_listener = threading.Thread(target=None)
t_init_flag = False
wait_for_init_start = True
lock = threading.Lock()

def handle(message):
    global listener, t_init_listener, t_init_flag, complete_stop, lock, main_breaker
    chat_id = message['chat']['id']

    t_username = None
    if 'from' in message:
        if 'username' in message['from']:
            t_username = message['from']['username']

    bot.sendMessage(chat_id, message['text'])
    command = message['text']
    if listener is None or command == '/start':
        print("handle: about to init")
        with lock:
            print("handle: locked")
            t_init_listener = threading.Thread(target=None)
            t_init_flag = False
            wait_for_init_start = True
            main_breaker = True
            time.sleep(5)
            listener = TelegramListener(bot, chat_id, t_username)
            t_init_listener = threading.Thread(target=listener.acquire_access_token)
            t_init_flag = True
            print("handle: about to unlock", wait_for_init_start, t_init_flag)

    elif command == stop_word:
        complete_stop = True

    listener.hears(command)


bot = telepot.Bot(bot_id)
bot.message_loop(handle)


print 'I am listening ...'
complete_stop = False
main_breaker = False

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

            # try:
            #     stdin = sys.stdin.read()
            #     if '\n' in stdin or '\r' in stdin:
            #         break
            # except IOError:
            #     pass
            if main_breaker or complete_stop:
                break
            time.sleep(1)
        self.main_runs = False
        if not complete_stop:
            self.loop_init()

t_main_loop = threading.Thread(target=Looper)
t_main_loop.start()
t_main_loop.join()
