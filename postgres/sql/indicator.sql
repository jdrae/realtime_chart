CREATE TABLE indicator (
    id SERIAL,
    symbol VARCHAR(20) NOT NULL,
    interval VARCHAR(10) NOT NULL,
    start_time BIGINT NOT NULL,

    label VARCHAR(20) NOT NULL,
    value NUMERIC(20, 10) NOT NULL,

    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC'),

    CONSTRAINT indicator_unique UNIQUE (label, symbol, interval, start_time) -- TODO: partitioning by label
);