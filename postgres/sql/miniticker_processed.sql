CREATE TABLE IF NOT EXISTS miniticker_processed (
    id SERIAL PRIMARY KEY,
    event_time BIGINT,          -- "E"
    symbol TEXT,                -- "s"
    open_price NUMERIC,         -- "o"
    close_price NUMERIC,        -- "c"
    high_price NUMERIC,         -- "h"
    low_price NUMERIC,          -- "l"
    volume_base NUMERIC,        -- "v"
    volume_quote NUMERIC,       -- "q"
    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC')
);