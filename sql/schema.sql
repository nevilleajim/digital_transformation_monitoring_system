
CREATE TABLE data_sources (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    source_url TEXT,
    retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    country_code CHAR(3) UNIQUE NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(100)
);


CREATE TABLE indicators (
    id SERIAL PRIMARY KEY,
    indicator_code VARCHAR(100) UNIQUE NOT NULL,
    indicator_name VARCHAR(255) NOT NULL,
    dimension VARCHAR(100) NOT NULL,
    definition TEXT,
    unit VARCHAR(100),
    source_id INTEGER REFERENCES data_sources(id),
    frequency VARCHAR(50),
    priority VARCHAR(20)
);


CREATE TABLE indicator_values (
    id BIGSERIAL PRIMARY KEY,

    country_id INTEGER NOT NULL
        REFERENCES countries(id),

    indicator_id INTEGER NOT NULL
        REFERENCES indicators(id),

    year INTEGER NOT NULL,

    value NUMERIC,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(country_id, indicator_id, year)
);


CREATE INDEX idx_indicator_values_country
ON indicator_values(country_id);

CREATE INDEX idx_indicator_values_indicator
ON indicator_values(indicator_id);

CREATE INDEX idx_indicator_values_year
ON indicator_values(year);