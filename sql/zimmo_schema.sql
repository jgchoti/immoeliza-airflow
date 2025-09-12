CREATE TABLE IF NOT EXISTS zimmo_data (
    id SERIAL,
    zimmo_code VARCHAR(255) PRIMARY KEY,
    type VARCHAR(100),
    sub_type VARCHAR(100),
    price DECIMAL(15, 2),
    street VARCHAR(255),
    number VARCHAR(20),
    postcode VARCHAR(20),
    city VARCHAR(100),
    living_area_m2 DECIMAL(10, 2),
    ground_area_m2 DECIMAL(10, 2),
    bedroom INTEGER,
    bathroom INTEGER,
    garage INTEGER,
    garden BOOLEAN,
    epc_kwh_m2 DECIMAL(10, 2),
    renovation_obligation BOOLEAN,
    year_built INTEGER,
    mobiscore DECIMAL(4,1),
    url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS zimmo_data_sample (
    id SERIAL,
    zimmo_code VARCHAR(255) PRIMARY KEY,
    type VARCHAR(100),
    sub_type VARCHAR(100),
    price DECIMAL(15, 2),
    street VARCHAR(255),
    number VARCHAR(20),
    postcode VARCHAR(20),
    city VARCHAR(100),
    living_area_m2 DECIMAL(10, 2),
    ground_area_m2 DECIMAL(10, 2),
    bedroom INTEGER,
    bathroom INTEGER,
    garage INTEGER,
    garden BOOLEAN,
    epc_kwh_m2 DECIMAL(10, 2),
    renovation_obligation BOOLEAN,
    year_built INTEGER,
    mobiscore DECIMAL(4,1),
    url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE scrape_summary (
    id SERIAL PRIMARY KEY,
    category_type VARCHAR(100),
    total_properties INTEGER,
    price_ranges_scraped INTEGER,
    duration_seconds DECIMAL(10,2),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_zimmo_city ON zimmo_data(city);
CREATE INDEX IF NOT EXISTS idx_zimmo_price ON zimmo_data(price);
CREATE INDEX IF NOT EXISTS idx_zimmo_type ON zimmo_data(type);
CREATE INDEX IF NOT EXISTS idx_zimmo_sub_type ON zimmo_data(sub_type);
CREATE INDEX IF NOT EXISTS idx_zimmo_postcode ON zimmo_data(postcode);
CREATE INDEX IF NOT EXISTS idx_zimmo_scraped_at ON zimmo_data(scraped_at);

ALTER TABLE zimmo_data
ALTER COLUMN number TYPE VARCHAR(50);