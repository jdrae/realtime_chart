CREATE TABLE IF NOT EXISTS miniticker_failed (
    id SERIAL PRIMARY KEY,
    source TEXT,
    payload JSONB NOT NULL,
    received_at TIMESTAMP DEFAULT NOW()
);