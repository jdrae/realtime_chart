CREATE TABLE IF NOT EXISTS miniticker_raw (
    id SERIAL PRIMARY KEY,
    source TEXT,
    payload JSONB NOT NULL,
    received_at TIMESTAMP DEFAULT NOW()
);