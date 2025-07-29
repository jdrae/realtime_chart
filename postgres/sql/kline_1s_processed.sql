CREATE TABLE IF NOT EXISTS kline_1s_processed (
    id SERIAL PRIMARY KEY,
    event_time         BIGINT,             -- "E": Event time (timestamp in ms)
    symbol             TEXT,               -- "s": Symbol
    is_closed          BOOLEAN,            -- "k.x": Is this kline closed?
    start_time   BIGINT,             -- "k.t": Kline start time
    close_time   BIGINT,             -- "k.T": Kline close time
    first_trade_id     BIGINT,             -- "k.f": First trade ID
    last_trade_id      BIGINT,             -- "k.L": Last trade ID
    open_price         NUMERIC,            -- "k.o": Open price
    close_price        NUMERIC,            -- "k.c": Close price
    high_price         NUMERIC,            -- "k.h": High price
    low_price          NUMERIC,            -- "k.l": Low price
    trade_count        BIGINT,            -- "k.n": Number of trades
    volume_base        NUMERIC,            -- "k.v": Base asset volume
    volume_quote       NUMERIC,            -- "k.q": Quote asset volume
    taker_volume_base NUMERIC,            -- "k.V": Taker buy base asset volume
    taker_volume_quote NUMERIC,           -- "k.Q": Taker buy quote asset volume
    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC'),

    CONSTRAINT unique_symbol_start_time UNIQUE (symbol, start_time)
);

CREATE INDEX idx_kline_1s_processed_start_time ON kline_1s_processed (start_time);
CREATE INDEX idx_kline_1s_processed_close_time ON kline_1s_processed (close_time);