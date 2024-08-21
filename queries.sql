DROP TABLE IF EXISTS public.tickers;

-- Recreate the table
CREATE TABLE public.tickers (
    id TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    instrument TEXT NOT NULL,
    symbol TEXT NOT NULL,
    type TEXT,
    strike FLOAT,
    expiry TIMESTAMPTZ,
    volume FLOAT NOT NULL,
    last_price FLOAT NOT NULL,
    side BOOLEAN NOT NULL,
    direction BOOLEAN,
    PRIMARY KEY (timestamp, instrument)
);

-- Create the hypertable
SELECT create_hypertable('public.tickers', 'timestamp');