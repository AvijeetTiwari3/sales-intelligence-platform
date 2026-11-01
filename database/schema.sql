-- Schema for Sales Intelligence & Analytics Platform
-- Compatible with SQLite and PostgreSQL

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS locations;

CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,
    region TEXT NOT NULL,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    postal_code TEXT,
    UNIQUE(country, region, state, city, postal_code)
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    sub_category TEXT NOT NULL,
    product_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    row_id INTEGER PRIMARY KEY,
    order_id TEXT NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    country TEXT NOT NULL,
    region TEXT NOT NULL,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    postal_code TEXT,
    sales REAL NOT NULL,
    quantity INTEGER NOT NULL,
    discount REAL NOT NULL,
    profit REAL NOT NULL,
    profit_margin REAL NOT NULL,
    shipping_days INTEGER NOT NULL,
    order_year INTEGER NOT NULL,
    order_month INTEGER NOT NULL,
    order_quarter INTEGER NOT NULL,
    year_month TEXT NOT NULL,
    is_profitable INTEGER NOT NULL,
    discount_tier TEXT NOT NULL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);

-- Performance Indexes for fast analytical aggregation
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_product ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region);
CREATE INDEX IF NOT EXISTS idx_orders_year_month ON orders(year_month);
CREATE INDEX IF NOT EXISTS idx_orders_category ON orders(row_id);
