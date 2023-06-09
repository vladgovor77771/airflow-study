from dataclasses import dataclass

@dataclass
class CandleInfo:
    market: str
    symbol: str
    timestamp_from: int
    timestamp_to: int
    open_price: float
    close_price: float
    high_price: float
    low_price: float
    volume: float
    trades_amount: int
