CREATE TABLE aggregated_kline_checkpoint
(
    id                SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    first_time        BIGINT NOT NULL,
    last_time        BIGINT NOT NULL,
    is_1m_aggregated  BOOLEAN                  DEFAULT FALSE,
    is_5m_aggregated  BOOLEAN                  DEFAULT FALSE,
    is_15m_aggregated BOOLEAN                  DEFAULT FALSE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_symbol_first_time_last_time UNIQUE (symbol, first_time, last_time)
);

CREATE INDEX idx_aggregated_kline_checkpoint_first_time ON aggregated_kline_checkpoint (first_time);
CREATE INDEX idx_aggregated_kline_checkpoint_last_time ON aggregated_kline_checkpoint (last_time);
