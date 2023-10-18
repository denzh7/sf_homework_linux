import json
import requests
from config import keys


class APIExceptionError(Exception):
    pass


class CryptoConverter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):

        if quote == base:
            raise APIExceptionError(f'Невозможно конвертировать одинаковую валюту "{base}"')

        try:
            quote_ticker = keys[quote]
        except KeyError:  # На основе ошибки KeyError поднимаем ошибку APIExceptionError
            raise APIExceptionError(f'Сори, валюту "{quote}" не конвертирую.\nСписок всех доступных валют: /values')

        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIExceptionError(f'Сори, валюту "{base}" не конвертирую.\nСписок всех доступных валют: /values')

        try:
            amount = float(amount)
        except ValueError:
            raise APIExceptionError(f'"{amount}" - это не верный ввод количества валюты.\n\
Пожалуйста, введите число')

        if float(amount) < 0:
            raise APIExceptionError(f'"{amount}" - это не верный ввод количества валюты.\n\
Пожалуйста, введите положительное число')

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}')
        total_base = json.loads(r.content)[keys[base]]

        return total_base*amount


