# Petpooja Sales Fetcher (Demo)

This repository contains a script to fetch sales data from the Petpooja API and store it into an SQLite database `sales_data.db`.

**NOTE:** Internet access and your API credentials are required to fetch real data. This demo run included below uses sample data to create `sales_data.db` so you can see the structure and test the workflow.

## Files
- `.env.` — for credentials (copy to `.env` and fill actual keys)
- `fetch_store_sales.py` — main script (supports `--demo` mode)
- `requirements.txt` — Python dependencies

## Setup (local)
```bash
git clone https://github.com/Deons2001/petpooja-sales.git
cd petpooja-sales
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env   # then edit .env with real credentials
python fetch_store_sales.py    # use real API when you have credentials
python fetch_store_sales.py --demo   # runs demo mode with sample data
```

## Git commands
```bash
git init
git add .
git commit -m "Add Petpooja sales fetcher (demo)"
git remote add origin https://github.com/Deons2001/petpooja-sales.git
git branch -M main
git push -u origin main
```


