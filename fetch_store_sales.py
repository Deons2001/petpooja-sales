#!/usr/bin/env python3
"""
fetch_store_sales.py
Fetches sales data from Petpooja API and stores into SQLite (sales_data.db).
"""

import os
import sqlite3
import logging
import requests
from requests.adapters import HTTPAdapter, Retry
from dotenv import load_dotenv

# Load .env values
load_dotenv()

BASE_URL = os.getenv("BASE_URL")
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REST_ID = os.getenv("REST_ID")
FROM_DATE = os.getenv("FROM_DATE")
TO_DATE = os.getenv("TO_DATE")
DB_FILE = os.getenv("DB_FILE", "sales_data.db")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Create DB table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sales_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    receipt_number TEXT,
    sale_date TEXT,
    transaction_time TEXT,
    sale_amount REAL,
    tax_amount REAL,
    discount_amount REAL,
    round_off REAL,
    net_sale REAL,
    payment_mode TEXT,
    order_type TEXT,
    transaction_status TEXT
);
"""

def ensure_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()

# Retry support for stable API calls
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.mount("http://", HTTPAdapter(max_retries=retries))

def fetch_sales_data():
    params = {
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "access_token": ACCESS_TOKEN,
        "restID": REST_ID,
        "from_date": FROM_DATE,
        "to_date": TO_DATE
    }

    logging.info("Calling Petpooja API...")
    response = session.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    return response.json()

def map_record(record):
    """Maps API record fields to DB schema (matches exact Petpooja fields)."""
    return (
        record.get("Receipt number"),
        record.get("Receipt Date"),
        record.get("Transaction Time"),
        float(record.get("Invoice amount", 0)),
        float(record.get("Tax amount", 0)),
        float(record.get("Discount amount", 0)),
        float(record.get("Round Off", 0).replace("+", "").replace("-", ""))  # clean +0.01 / -0.01
        if isinstance(record.get("Round Off"), str) else float(record.get("Round Off", 0)),
        float(record.get("Net sale", 0)),
        record.get("Payment Mode"),
        record.get("Order Type"),
        record.get("Transaction status")
    )

def insert_rows(rows):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO sales_data (
            receipt_number, sale_date, transaction_time,
            sale_amount, tax_amount, discount_amount,
            round_off, net_sale, payment_mode,
            order_type, transaction_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()

def main():
    ensure_db()

    data = fetch_sales_data()

    # Real API uses "Records" (Capital R)
    records = data.get("Records") or data.get("records")

    if not records:
        logging.error("Could not find sales records in API response.")
        print("FULL JSON Response:", data)
        return

    rows = [map_record(rec) for rec in records]
    insert_rows(rows)

    logging.info(f"Inserted {len(rows)} rows into sales_data.db")

if __name__ == "__main__":
    main()
