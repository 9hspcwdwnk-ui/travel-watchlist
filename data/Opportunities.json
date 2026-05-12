# Travel Arbitrage Command Center

This is the automated starter version.

## What it does now

- Hosts a free static dashboard on GitHub Pages.
- Reads opportunities from `data/opportunities.json`.
- Runs a scheduled GitHub Actions Python script.
- Re-scores and refreshes the board automatically.
- Can later connect to Seats.aero Pro API, fare APIs, and transfer bonus sources.

## Files

- `index.html` — dashboard
- `data/opportunities.json` — live opportunity data
- `scripts/update_watchlist.py` — automated scanner/scoring script
- `.github/workflows/update-watchlist.yml` — scheduled GitHub Actions automation
- `config.json` — your airports, rules, and target destinations

## Setup

1. Upload all files/folders to your GitHub repo.
2. In GitHub, go to Settings → Pages.
3. Source: Deploy from branch.
4. Branch: main.
5. Folder: /root.
6. Save.

## Test automation

Go to Actions → Update Travel Watchlist → Run workflow.

If it works, `data/opportunities.json` will update with a fresh timestamp.

## Next serious upgrade

Add API integrations:
- Seats.aero Pro API for award availability.
- Transfer bonus monitoring.
- Fare monitoring source.

API keys should be stored in GitHub:
Settings → Secrets and variables → Actions → New repository secret.

Never place API keys directly in code.
