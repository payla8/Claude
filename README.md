# GameStop Digital Products Scraper

A web scraper and dashboard for GameStop digital game products with price calculations and AllKeyShop price comparison.

## Features

- **Complete Digital Catalog**: Scrapes ~4800 digital products from GameStop
- **Platform Filtering**: Xbox, Nintendo, PC (PlayStation excluded - GameStop doesn't sell PS digital codes)
- **Price Calculations**:
  - Regular price
  - Pro membership discount (5% off)
  - Your cost with GameStop card discount (configurable, default 0.88)
  - USD to EUR conversion with live exchange rates
- **AllKeyShop Integration**: Compare prices with AllKeyShop marketplace
- **Excel Export**: Export filtered results to Excel spreadsheet
- **Live Dashboard**: Interactive HTML interface with search, sorting, and filtering

## API Endpoints

- `GET /health` - Health check
- `GET /rate` - Get current USD/EUR exchange rate
- `GET /scrape` - Scrape all digital products
  - Query params: `discount_rate` (default 0.88), `max_pages` (default 0 = all)
- `GET /scrape/quick` - Quick sample (3 pages)
  - Query params: `pages` (default 3), `discount_rate`
- `GET /allkeyshop/price` - Fetch lowest price from AllKeyShop
  - Query params: `url`, `edition`, `region`, `keys_only`

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **APIs**: Constructor.io (GameStop's catalog API), Google Finance (exchange rates)
- **Deployment**: Render.com

## Local Development

1. Install dependencies:
```bash
pip install -r gamestop_requirements.txt
```

2. Run the API server:
```bash
python gamestop_scraper_api.py
```

3. Open `gamestop_scraper.html` in your browser

4. Set API URL to `http://localhost:8000`

## Deployment to Render.com

1. Push code to GitHub repository

2. Create new Web Service on Render.com:
   - Connect your GitHub repository
   - Use `render.yaml` for configuration (auto-detected)
   - Or manually configure:
     - Build Command: `pip install -r gamestop_requirements.txt`
     - Start Command: `uvicorn gamestop_scraper_api:app --host 0.0.0.0 --port $PORT`

3. Update `gamestop_scraper.html` with your Render.com API URL

## Data Source

Uses Constructor.io API (`ac.cnstrc.com`) - GameStop's official search/catalog provider. The `digital-store` group contains all digital products (~4824 items).

## Notes

- GameStop does NOT sell PlayStation digital codes, only physical discs. All PlayStation products are automatically filtered out.
- The Constructor.io API returns base/list prices. Promotional prices (like "Digital condition $28") are only available on product pages and not accessible via API.
- AllKeyShop prices include payment fees (`priceCard` field) for accurate price comparison.

## Version

v4.0.0 - PlayStation filtering, digital-store group, AllKeyShop price card accuracy
