CREATE TABLE IF NOT EXISTS indicator_failed (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    error TEXT NULL,
    created_at TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC')
);