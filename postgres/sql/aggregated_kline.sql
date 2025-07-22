CREATE TABLE aggregated_kline (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    start_time BIGINT NOT NULL,
    close_time BIGINT NOT NULL,
    row_count INTEGER NOT NULL,

    open_price NUMERIC(20, 10) NOT NULL,
    close_price NUMERIC(20, 10) NOT NULL,
    high_price NUMERIC(20, 10) NOT NULL,
    low_price NUMERIC(20, 10) NOT NULL,

    trade_count BIGINT NOT NULL,

    volume_base NUMERIC(30, 10) NOT NULL,
    volume_quote NUMERIC(30, 10) NOT NULL,

    taker_volume_base NUMERIC(30, 10) NOT NULL,
    taker_volume_quote NUMERIC(30, 10) NOT NULL,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_symbol_interval_start_time UNIQUE (symbol, interval, start_time)
);

CREATE INDEX idx_aggregated_kline_start_time ON aggregated_kline (start_time);
CREATE INDEX idx_aggregated_kline_close_time ON aggregated_kline (close_time);
