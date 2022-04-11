import telebot

from game import Game
from player import Player


# Connecting to bot
token = '1596019737:AAGejLssYYthYSPjB04rXDu46s6tH8tAjV8'    # trinka bot
# token = '5164717156:AAG1wDC7PvSHR8jlxEDLsJ_lxmXTZkgrOlw'    # poker bot
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    """Send greeting message"""
    msg = """ Hello, I can start a poker match for you
If you want to play just type /play in chat with other players"""
    bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['play'])
def play_message(message):
    """React to person's desire to play"""
    game = Game(bot)
    game.chat = message.chat.id
    new_player = Player(message.from_user)
    game.add_player(new_player)
    game.current_message = bot.send_message(message.chat.id, game.message_text, reply_markup=game.markup)
    game.handle_callbacks()


bot.infinity_polling()

