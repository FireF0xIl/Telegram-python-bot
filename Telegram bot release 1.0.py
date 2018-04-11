from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import requests


def start(bot, updater):
    updater.message.reply_text("Какой город интересует?")
    return 1


def help(bot, updater):
    updater.message.reply_text("Я бот-справочник по географическим объектам и организациям.")


def stop(bot, update):
    update.message.reply_text(
        "Жаль. А было бы интерсно пообщаться. Всего доброго!")
    return ConversationHandler.END  # Константа, означающая конец диалога.


def close(bot, upadter):
    upadter.message.reply_text("OK", reply_markup=ReplyKeyboardRemove())
    return 2


def city(bot, updater, user_data):
    user_data["map"] = {"geocode": updater.message.text, "format": "json"}
    user_data["map_search_server"] = "http://geocode-maps.yandex.ru/1.x/"
    updater.message.reply_text("Что рассказать про {}?".format(user_data["map"]["geocode"]), reply_markup=info)
    return 2


def text(bot, updater):
    updater.message.reply_text("Введена неверная команда, пожалуйста, повторите ввод")
    return 2


def show_map(bot, updater, user_data):
    log = open("log", mode="a+")
    log.write(str(user_data)+"\n")
    log.close()
    response = requests.get(user_data["map_search_server"], params=user_data["map"])
    try:
        toponym = response.json()["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        log = open("log", mode="a+")
        log.write(str(toponym_coodrinates) + "\n")
        log.close()
        address_ll = ",".join(toponym_coodrinates.split())
        if user_data["map"].get("pt", "") == "":
            user_data["map"]["pt"] = address_ll + ",org"
        else:
            user_data["map"]["pt"] = user_data["map"]["pt"] + "~" + address_ll + ",org"

        static_api_request = "http://static-maps.yandex.ru/1.x/?l=map&pt={}".format(user_data["map"]["pt"])
        updater.message.reply_text("Запрос выполнен")
        bot.sendPhoto(
            updater.message.chat.id,  # Идентификатор чата. Куда посылать картинку.
            # Ссылка на static API по сути является ссылкой на картинку.
            static_api_request
        )
    except:
        updater.message.reply_text("Объект не найден. Объект поиска очищен, повторите ввод")
        user_data["map"]["geocode"] = ""
        return 1


def geo_object(bot, updater):
    updater.message.reply_text("Какие объекты поискать?", reply_markup=ReplyKeyboardRemove())
    return "1 geo"


def add_object(bot, updater, user_data):

    return


def toponym_object(bot, updater, user_data):
    user_data["map"]["geocode"] += "," + updater.message.text
    updater.message.reply_text("Показать карту?", reply_markup=bool_markup)
    return "show_map"


def org_object(bot, updater, user_data):
    pass


def show(bot, updater, user_data):
    if updater.message.text.lower() == "yes" or updater.message.text == "+":
        show_map(bot, updater, user_data)
        return 2
    elif updater.message.text.lower() == "no" or updater.message.text == "-":
        updater.message.reply_text("Что ещё показать?", reply_markup=ReplyKeyboardRemove())
        return "1 geo"
    else:
        updater.message.reply_text("Ошибка в команде, повторите ввод.", reply_markup=bool_markup)
        return "show_map"


def main():
    # Создаем объект updater. Вместо слова "TOKEN" надо разместить полученнй от @BotFather токен
    updater = Updater("505790424:AAGcBopeCJGDyqytoM15tgca_5IJ6LEyncE")
    # Получаем из него диспетчер сообщений.
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        # Без изменений
        entry_points=[CommandHandler('start', start)],

    states = {
        # Добавили user_data для сохранения ответа.
        1: [MessageHandler(Filters.text, city, pass_user_data=True)],
        2: [MessageHandler(Filters.text, text)],
        "1 geo": [MessageHandler(Filters.text, toponym_object, pass_user_data=True)],
        "show_map": [MessageHandler(Filters.text, show, pass_user_data=True)]
    },

    fallbacks = [CommandHandler('stop', stop), CommandHandler("Показать_карту", show_map, pass_user_data=True),
                 CommandHandler('Поиск_по_геобъекту', geo_object),
                 CommandHandler('Поиск_по_организации', org_object, pass_user_data=True)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("close", close))
    dp.add_handler(CommandHandler("help", help))

    # Запускаем цикл приема и обработки сообщений.
    updater.start_polling()
    # Ждем завершения приложения. (например, получение сигнала SIG_TERM при нажатии клавиш Ctrl+C)
    updater.idle()


info_keyboard = [["/Поиск_по_геобъекту", "/Поиск_по_организации"],
                 ["/Показать_карту"],
                 ["/stop"]]

bool_keyboard = [
    ["Yes", "No"]
]

info = ReplyKeyboardMarkup(info_keyboard, one_time_keyboard=False)
bool_markup = ReplyKeyboardMarkup(bool_keyboard, one_time_keyboard=True)
# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
