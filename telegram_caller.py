import sys
import io
import telepot
import time
import json
from telegram_listener import TelegramListener


activeListeners = dict()

with open('secret//bot_secret.json', 'r') as file:
    data = json.load(file)
    bot_id = data['bot_id']
    stop_word = data['stop_word']

commands = ['/login', '/start', '/show_playlists', '/all', '/yes', '/no' '/finish']


def handle(message):
    global complete_stop
    if message['text'] == stop_word:
        complete_stop = True

    chat_id = message['chat']['id']
    if chat_id not in activeListeners.keys():
        activeListeners[chat_id] = TelegramListener(bot, chat_id)

    command = message['text']
    if command in commands:
        if command == '/start':
            activeListeners[chat_id].login_start()
            if activeListeners[chat_id].is_authorized():
                activeListeners[chat_id].login_finish()
        elif command == '/show_playlists':
            activeListeners[chat_id].show_playlists()
        elif command == '/all':
            activeListeners[chat_id].all()
    else:
        activeListeners[chat_id].hear_word(command)

    bot.sendMessage(chat_id, command)


bot = telepot.Bot(bot_id)
bot.message_loop(handle)

print('I am listening ...')

complete_stop = False
while True:
    for chat_id_debug in activeListeners.keys():
        print("chat: {0}, state: {1}".format(chat_id_debug, str(activeListeners[chat_id_debug].state)))
    if complete_stop:
        break
    time.sleep(1)
