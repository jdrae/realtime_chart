CREATE TABLE IF NOT EXISTS miniticker_failed (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    error TEXT NULL,
    received_at TIMESTAMP DEFAULT NOW()
);