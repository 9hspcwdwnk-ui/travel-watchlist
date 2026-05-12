# Travel Arbitrage Watchlist

Simple/free setup:

- `index.html` = private-ish dashboard
- `opportunities.csv` = live opportunity board
- `update_watchlist.py` = local Python helper to add opportunities

## Free hosting option

Use GitHub Pages.

1. Create a GitHub account if needed.
2. Create a new repository, for example: `travel-watchlist`.
3. Upload:
   - `index.html`
   - `opportunities.csv`
   - `update_watchlist.py`
4. Go to repository Settings → Pages.
5. Set source to `main` branch and `/root`.
6. Your site will publish at a GitHub Pages URL.
7. Optional: connect your own domain later.

## Daily workflow

When an alert finds something good:

1. Open Terminal in this folder.
2. Run:

```bash
python3 update_watchlist.py
```

3. Enter the details.
4. Commit/push to GitHub:

```bash
git add opportunities.csv
git commit -m "Update travel opportunities"
git push
```

GitHub Pages will republish the dashboard.

## Important privacy note

Free GitHub Pages is best treated as public-facing unless you use a paid/private setup or protect it behind another service. Do not put passport numbers, account logins, Amex details, booking confirmation numbers, or sensitive personal information in the CSV.
