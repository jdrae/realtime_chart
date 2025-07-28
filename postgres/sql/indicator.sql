CREATE TABLE indicator (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    start_time BIGINT NOT NULL,

    label VARCHAR(20) NOT NULL,
    value NUMERIC(20, 10) NOT NULL,

    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC'),

    CONSTRAINT unique_symbol_interval_start_time_key UNIQUE (symbol, interval, start_time, label)
) PARTITION BY LIST (indicator);

CREATE TABLE indicator_ma_7 PARTITION OF indicator
    FOR VALUES IN ('ma_7');

CREATE TABLE indicator_ma_20 PARTITION OF indicator
    FOR VALUES IN ('ma_20');