import logging
import requests
import telegram
from bs4 import BeautifulSoup
from telegram import Update,ParseMode,KeyboardButton,ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, Updater, InlineQueryHandler,CallbackQueryHandler
from imdb import IMDb
import imdb
import json
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
import re

import os
PORT = int(os.environ.get('PORT', 5000))


def start(update:Update, callback:CallbackContext):
    buttons = [[KeyboardButton("/Start")], [KeyboardButton("🔎Search")], [KeyboardButton("/Favorites")]]
    callback.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to moviefinder bot!",reply_markup=ReplyKeyboardMarkup(buttons))

    buttonss = [[InlineKeyboardButton("Favorites", callback_data="list")],[InlineKeyboardButton("search", callback_data="searcher")]]
    callback.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttonss), text=f"Choose one below to continue👇")


def list(update:Update, callback:CallbackContext):
    buttons = [[KeyboardButton("/Start")], [KeyboardButton("🔎Search")], [KeyboardButton("/Favorites")]]
    Favorites = read_json()
    username = update.effective_user.username
    print(username)

    if username not in Favorites.keys():
        callback.bot.send_message(chat_id=update.effective_chat.id, text="List is empty!",reply_markup=ReplyKeyboardMarkup(buttons))

    else:
        favorite = ""
        for fav in Favorites[username]:
            favorite += fav + "\n"
        callback.bot.send_message(chat_id=update.effective_chat.id, text=f"{favorite}",reply_markup=ReplyKeyboardMarkup(buttons))







def find(update: Update, callback: CallbackContext):
    buttons = [[KeyboardButton("/Start")], [KeyboardButton("🔎Search")], [KeyboardButton("/Favorites")]]
    text = update.message.text
    if text == "🔎Search":
        callback.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the movie name.", reply_markup=ReplyKeyboardMarkup(buttons))

    else:
        ia = imdb.IMDb()
        newids = {}
        movies = ia.search_movie(update.message.text)
        q = 0
        for movie in movies:
            if q < 5:
                q += 1
                newids[movie["title"]] = movie.movieID
                try:
                    infbutton = [[InlineKeyboardButton("🎬 more information", callback_data=f"inf{movie.movieID}")]]
                    # update.message.reply_text(f"{movie} {movie['year']}")
                    callback.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(infbutton), text=f"{movie} {movie['year']}")
                    # print(update.effective_message)
                    # print(callback.bot_data)

                except KeyError:
                    # update.message.reply_text(f"{movie}")
                    infbutton = [[InlineKeyboardButton("🎬 more information", callback_data=f"inf{movie.movieID}")]]
                    callback.bot.send_message(chat_id=update.effective_chat.id,
                                              reply_markup=InlineKeyboardMarkup(infbutton),
                                              text=f"{movie}")
                except:
                    update.message.reply_text(f"try again😔")


            # callback.bot_data.update({"idsdict": newids})
            # update.message.reply_text("جهت دریافت اطلاعات در باره فیلم نام فیلم مورد نظر را وارد نمایید. و در انتهای نام فیلم .inf را اضافه کنید.")

        # else:
        #
        #     chosenmovie = update.message.text
        #     chosenmovie = chosenmovie.replace(".inf", "")
        #     print(callback.bot_data)
        #     try:
        #         movieid = callback.bot_data["idsdict"][chosenmovie]
        #         print(movieid)
        #     except KeyError:
        #         update.message.reply_text("نام وارد شده یافت نشد.")
        #         return
        #     ia = IMDb()
        #     movie = ia.get_movie(movieid)
        #
        #     try:
        #         country = ""
        #         for count in movie['countries']:
        #             country = count['name'] + " "
        #     except:
        #         country = "-"
        #     try:
        #         genre = ""
        #         for gen in movie['countries']:
        #             country = gen['name'] + " "
        #     except:
        #         genre = "-"
        #
        #     try:
        #         language = ""
        #         for lan in movie['countries']:
        #             country = lan['name'] + " "
        #     except:
        #         language = "-"
        #
        #     try:
        #         dirct = ""
        #         for director in movie['directors']:
        #             dirct = director['name'] + " "
        #
        #     except:
        #         dirct ="-"
        #
        #     buttons = [[InlineKeyboardButton("🤩 Add to favorite list", callback_data="favorite")],
        #                [InlineKeyboardButton("👍", callback_data="like")],
        #                [InlineKeyboardButton("👎", callback_data="dislike")]]
        #     callback.bot.send_message(chat_id=update.effective_chat.id,reply_markup=InlineKeyboardMarkup(buttons),text=f"genres: {genre}\ncountry: {country}\nrelease year: {movie['year']}\nlanguage: {language}\ndirector: {dirct}")

            # buttons = [[InlineKeyboardButton("Add to favorite list", callback_data="like")],
            #            [InlineKeyboardButton("Add to download list", callback_data="dislike")]]
            # callback.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons))


def queryHandler(update: Update, callback: CallbackContext):
    query = update.callback_query.data
    update.callback_query.answer()

    global likes, dislikes

    if "searcher" in query:
        callback.bot.send_message(chat_id=update.effective_chat.id, text=f"Please enter the movie name:")


    elif "list" in query:

        Favorites = read_json()
        username = update.effective_user.username

        if username not in Favorites.keys():
            callback.bot.send_message(chat_id=update.effective_chat.id, text="List is empty!")

        else:
            favorite = ""
            for fav in Favorites[username]:
                favorite += fav + "\n"
            callback.bot.send_message(chat_id=update.effective_chat.id, text=f"{favorite}")




    elif "inf" in query:
        movieid = update.callback_query.data
        movieid = movieid.replace("inf", "")
        ia = IMDb()
        movie = ia.get_movie(movieid)

        try:
            country = ""
            for count in movie["countries"]:
                country += count + " "
        except:
            country = "-"

        try:
            genre = ""
            for gen in movie["genres"]:
                genre += gen + " "
        except:
            genre = "-"

        try:
            language = ""
            for lan in movie["languages"]:
                language += lan + " "
        except:
            language = "English"

        try:
            dirct = ""
            for director in movie['directors']:
                dirct += director['name'] + " "

        except:
            dirct = "-"

        try:
            qq= 0
            actor = ""
            for act in movie["actors"]:
                if qq < 5:
                    actor += act["name"] + " "
                    qq += 1
        except:
            actor = "-"

        try:
            qqq = 0
            writer = ""
            for writ in movie["writer"]:
                if qqq < 3:
                    writer += writ["name"] + " "
                    qqq += 1
        except:
            writer = "-"

        try:
            year = movie['year']
        except:
            year = "-"

        buttons = [[InlineKeyboardButton("🤩 Add to Favorites", callback_data="add")]]

        callback.bot.send_message(chat_id=update.effective_chat.id, reply_markup=InlineKeyboardMarkup(buttons),
                text=f"🎞Title: {movie['title']}\n🍿Genres: {genre}\n🏳Country: {country}\n📅Release Year: {year}\n👅Language: {language}\n🎬Director: {dirct}\n🎥Actors: {actor}\n✍️Writer: {writer}")

    if "add" in query:
        Favorites = read_json()
        username = update.effective_user.username
        movieinf = update.callback_query["message"]["text"]
        print(movieinf)

        if username not in Favorites.keys():
            Favorites[username] = []

        Favorites[username].append(movieinf)
        Favorites[username].append("\n")
        write_json(Favorites)




def write_json(data, filename="Favorites.json"):
    with open(filename, 'w') as target:
        json.dump(data, target, indent=4, ensure_ascii=False)


def read_json(filename="Favorites.json"):
    with open(filename, 'r') as target:
        data = json.load(target)
    return data


try:
    read_json()
except:
    write_json({})





def main():
    updater = Updater("5212438580:AAHc4UgpGC7ql2nq2cE1sxuoJE7QXUgwEsQ")
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("Start", start))
    dispatcher.add_handler(CommandHandler("Favorites", list))
    dispatcher.add_handler(MessageHandler(Filters.text, find))
    dispatcher.add_handler(CallbackQueryHandler(queryHandler))

    updater.start_webhook(listen="0.0.0.0",port=int(PORT), url_path="5212438580:AAHc4UgpGC7ql2nq2cE1sxuoJE7QXUgwEsQ")
    updater.bot.setWebhook('https://moviefindeproject1.herokuapp.com/' + "5212438580:AAHc4UgpGC7ql2nq2cE1sxuoJE7QXUgwEsQ")


    updater.idle()





if __name__ == "__main__":
    main()


# check these errors
# imdb._exceptions.IMDbDataAccessError check this error
# ValueError: Command is not a valid bot command
