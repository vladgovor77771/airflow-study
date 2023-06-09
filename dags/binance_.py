from binance import Client
from datetime import datetime, timedelta
from candle import CandleInfo


BINANCE_SECRET_KEY="somesecretkey"
BINANCE_API_KEY="someapikey"

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)


def get_candles(symbol: str, limit=1):
    res = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, limit=limit)
    return list(map(lambda x: CandleInfo("binance", symbol.lower(), int(x[0] / 1000), int(x[6] / 1000), x[1], x[4], x[2], x[3], x[5], x[8]), res))


def check_alive():
    return True
