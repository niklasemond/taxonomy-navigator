CREATE TABLE IF NOT EXISTS top_global_firms (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    naics_codes VARCHAR(255),
    revenue DECIMAL(15,2),
    market_cap DECIMAL(15,2),
    market_share DECIMAL(5,2),
    yoy_growth DECIMAL(5,2)
);

-- Create an index on naics_codes for faster searching
CREATE INDEX IF NOT EXISTS idx_naics_codes ON top_global_firms(naics_codes); 