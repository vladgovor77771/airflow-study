CREATE SCHEMA IF NOT EXISTS crypto;

CREATE TABLE IF NOT EXISTS crypto.candles (
    market TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timestamp_from BIGINT NOT NULL,
    timestamp_to BIGINT NOT NULL,
    open_price DOUBLE PRECISION NOT NULL,
    close_price DOUBLE PRECISION NOT NULL,
    high_price DOUBLE PRECISION NOT NULL,
    low_price DOUBLE PRECISION NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    trades_amount BIGINT NOT NULL
);
