import requests
from candle import CandleInfo


def get_candles(symbol: str, limit=2):
    res = requests.get(f'https://api.huobi.pro/market/history/kline?symbol={symbol.lower()}&period=1min&size={limit}')
    return list(map(lambda x: CandleInfo("huobi", symbol.lower(), x['id'], x['id'] + 60, x['open'], x['close'], x['high'], x['low'], x['vol'], x['count']), res.json()['data']))


def check_alive():
    return True
