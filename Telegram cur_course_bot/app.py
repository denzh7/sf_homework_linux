""" Telegram-бот cur_course_bot
Ссылка на телеграм бот: t.me/cur_course_bot
Бот возвращает цену на определённое количество валюты (евро, доллар или рубль).

При написании бота использована библиотека pytelegrambotapi.
Для получения курса валют пользователь должен отправить сообщение боту в виде:
    <имя валюты, цену которой он хочет узнать> <имя валюты, в которой надо узнать цену первой валюты>
    <количество первой валюты>.
При вводе команды /start или /help пользователю выводятся инструкции по применению бота.
При вводе команды /values выводиться информация о всех доступных валютах в читаемом виде.

Для получения курса валют используется API https://min-api.cryptocompare.com/documentation
запросы отправляются с помощью библиотеки Requests.
Для парсинга полученных ответов используется библиотека JSON.

При ошибке пользователя (например, введена неправильная или несуществующая валюта или неправильно введено число)
вызывается исключение APIExceptionError с текстом пояснения ошибки.
Текст любой ошибки с указанием типа ошибки должен отправляться пользователю в сообщения.
Для отправки запросов к API описан класс  CryptoConverter со статическим методом get_price(),
который принимает три аргумента и возвращает нужную сумму в валюте:
    имя валюты, цену на которую надо узнать, — base;
    имя валюты, цену в которой надо узнать, — quote;
    количество переводимой валюты — amount.

Токен Telegram-бота хранится в файле config.py.
Классы в файле extensions.py.

"""

import telebot
import emoji
from config import TOKEN, keys, text_for_user, excess_parameters, not_enough_parameters
from extensions import APIExceptionError, CryptoConverter

bot = telebot.TeleBot(TOKEN)
emo = emoji.emojize


@bot.message_handler(commands=['help', 'start'])
def command_help(message: telebot.types.Message):
    bot.reply_to(message, text_for_user)


@bot.message_handler(commands=['values'])
def command_values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for key in keys.keys():
        text = '\n'.join((text, key,))
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text', ])
def convert(message: telebot.types.Message):
    try:
        values = message.text.lower().replace(',', '.').split(' ')

        if len(values) > 3:
            raise APIExceptionError(excess_parameters)
        elif len(values) < 2:
            raise APIExceptionError(not_enough_parameters)
        elif len(values) == 2:
            values.append('1')

        quote, base, amount = values
        total_base = CryptoConverter.get_price(quote, base, amount)
    except APIExceptionError as e:
        bot.reply_to(message, emo(f'Что то пошло не так 🤷🏻‍♂️\n{e}'))
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'Цена {amount} {quote} в {base} - {total_base}'
        bot.send_message(message.chat.id, text)


bot.polling()
