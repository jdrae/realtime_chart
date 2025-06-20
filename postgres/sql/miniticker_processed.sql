CREATE TABLE IF NOT EXISTS miniticker_processed (
    id SERIAL PRIMARY KEY,
    event_time BIGINT,          -- "E"
    symbol TEXT,                -- "s"
    close_price NUMERIC,        -- "c"
    open_price NUMERIC,         -- "o"
    high_price NUMERIC,         -- "h"
    low_price NUMERIC,          -- "l"
    volume_base NUMERIC,        -- "v"
    volume_quote NUMERIC,       -- "q"
    received_at TIMESTAMP DEFAULT NOW()
);