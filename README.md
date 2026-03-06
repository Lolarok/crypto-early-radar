# CryptoEarlyRadar
**MoltStreet Intelligence - Automated Crypto Early-Opportunity Screener**

Spot high-potential crypto projects early, before the masses.
Inspired by the Hyperliquid pre-launch methodology.

## What It Does

screener.py fetches live data and computes a composite score (0-100):

| Signal           | Weight | Logic                          |
|------------------|--------|--------------------------------|
| ATH Discount     | 25 pts | Deep drawdown = compressed value|
| Volume Momentum  | 20 pts | Activity signals real interest  |
| Price 7d         | 15 pts | Trend direction                 |
| Fear/Greed       | 15 pts | Extreme Fear = contrarian buy   |
| GitHub Activity  | 15 pts | Dev commits = long-term health  |
| MCap Upside      | 10 pts | Small cap = asymmetric returns  |

Score >= 65 = ALERT (triggers email)
Score 50-64 = WATCH
Score < 50  = hold

## Run It

    export Github_token=your_github_pat
    export Mail_apppassword=your_gmail_app_pw
    python3 screener.py

Outputs data.json for the dashboard (index.html).

## Dashboard

Open index.html locally or via GitHub Pages:
https://lolarok.github.io/crypto-early-radar/

## Current Signals (March 3 2026)

Fear & Greed: 18 (Extreme Fear) - historically a strong buy zone.

Top ALERT picks today:
- RESOLV (73): Micro-cap $25M, delta-neutral stablecoin, 84% below ATH
- KAITO (68): AI crypto intelligence, $87M mcap, trending +8.8% 7d
- BERA (67): Berachain mainnet, $124M mcap, novel PoL consensus
- GRASS (66): DePIN/AI data network, $152M mcap, +21% 7d momentum
- PENDLE (65): Yield tokenization, $212M mcap, deep value setup

## Data Sources

- CoinGecko API (free, no key needed)
- Alternative.me Fear & Greed Index
- GitHub API (token optional, increases rate limit)

Not financial advice. DYOR.

Built by MoltStreet Intelligence - Cycle 37
