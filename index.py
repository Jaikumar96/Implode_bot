import os
from io import BytesIO
from queue import Queue
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie

TOKEN = os.getenv("TOKEN")
URL = "https://implode-bot.vercel.app"
bot = Bot(TOKEN)

def welcome(update, context) -> None:
    try:
        update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to SB Movies.\n"
                                  f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
        update.message.reply_text("👇 Enter Movie Name 👇")
    except Exception as e:
        print(f"An error occurred in 'welcome' function: {e}")

def find_movie(update, context):
    try:
        search_results = update.message.reply_text("Processing...")
        query = update.message.text
        movies_list = search_movies(query)
        if movies_list:
            keyboards = []
            for movie in movies_list:
                keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
                keyboards.append([keyboard])
            reply_markup = InlineKeyboardMarkup(keyboards)
            search_results.edit_text('Search Results...', reply_markup=reply_markup)
        else:
            search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name.')
    except Exception as e:
        print(f"An error occurred in 'find_movie' function: {e}")

def movie_result(update, context) -> None:
    try:
        query = update.callback_query
        s = get_movie(query.data)
        response = requests.get(s["img"])
        img = BytesIO(response.content)
        query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
        link = ""
        links = s["links"]
        for i in links:
            link += "🎬" + i + "\n" + links[i] + "\n\n"
        caption = f"⚡ Fast Download Links :-\n\n{link}"
        if len(caption) > 4095:
            for x in range(0, len(caption), 4095):
                query.message.reply_text(text=caption[x:x+4095])
        else:
            query.message.reply_text(text=caption)
    except Exception as e:
        print(f"An error occurred in 'movie_result' function: {e}")

def setup():
    try:
        update_queue = Queue()
        dispatcher = Dispatcher(bot, update_queue, use_context=True)
        dispatcher.add_handler(CommandHandler('start', welcome))
        dispatcher.add_handler(MessageHandler(Filters.text, find_movie))
        dispatcher.add_handler(CallbackQueryHandler(movie_result))
        return dispatcher
    except Exception as e:
        print(f"An error occurred in 'setup' function: {e}")

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/{}'.format(TOKEN), methods=['GET', 'POST'])
def respond():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        setup().process_update(update)
        return 'ok'
    except Exception as e:
        print(f"An error occurred in 'respond' function: {e}")
        return 'error'

@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    try:
        s = bot.setWebhook('{URL}/{HOOK}'.format(URL=URL, HOOK=TOKEN))
        if s:
            return "webhook setup ok"
        else:
            return "webhook setup failed"
    except Exception as e:
        print(f"An error occurred in 'set_webhook' function: {e}")

