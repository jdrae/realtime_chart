CREATE TABLE IF NOT EXISTS kline_1s_raw (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC')
);