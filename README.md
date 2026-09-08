🇬🇧 English | [🇫🇷 Français](README.fr.md)

# Market Notes — Cross-Asset Market Dashboard

A cross-asset market monitoring tool that automates data collection, risk indicator calculations, and the generation of a structured market note —
in the style of a trading desk's morning note.

## Why this project

As a finance master's student targeting front office roles in financial markets (sales or trading), I built this tool to reproduce, at my own scale, 
a daily practice of the job: gathering information, identifying significant moves, and building rigorous macro reasoning rather than forcing narrative 
explanations.

## Instruments tracked (core set)

| Instrument | Ticker (Yahoo Finance) | Asset class |
|---|---|---|
| US 10Y Yield | `^TNX` | Rates |
| EUR/USD | `EURUSD=X` | FX |
| S&P 500 | `^GSPC` | Equities |
| Gold | `GC=F` | Commodities |
| Crude Oil (WTI) | `CL=F` | Commodities |

### Why these instruments?

The choice is a deliberately **cross-asset**, restricted basket rather than a single asset class, for two reasons:
- **Avoiding dilution**: tracking too many instruments from the start pushes toward superficial observations on each one rather than a rigorous
  analysis on a few.
- **Capturing cross-market dynamics**: these 5 instruments allow for coherent macro narratives between them (e.g., rising US yields feeding through
  to a stronger dollar, which in turn weighs on gold and risk assets) — a cross-asset reasoning central to market reading in macro sales or trading.

Each instrument acts as a barometer for its asset class:
- **US 10Y Yield**: the reference point for the rates market, closely watched because it influences nearly every other asset class
- **EUR/USD**: the most liquid currency pair, sensitive to rate differentials and global risk sentiment
- **S&P 500**: the most widely watched equity benchmark globally
- **Gold**: the classic safe-haven asset, often used as a risk-on/risk-off sentiment gauge
- **Crude Oil (WTI)**: reflects both global economic demand and geopolitical tensions

This list isn't fixed: the project allows adding a one-off "focus" instrument (e.g., a specific stock) in response to a particular event, without altering 
the permanent core set.

## Data source

All market data is retrieved via **Yahoo Finance** (`yfinance` library), free and requiring no API key. This is a practical source for a student project, 
but it has limitations compared to a professional terminal (Bloomberg, Refinitiv) — see "Known limitations" below.

## Architecture

```
market-notes/
├── src/
│   ├── data_fetch.py      # Price retrieval and cleaning (Yahoo Finance)
│   ├── analysis.py         # Multi-horizon returns, volatility, correlations
│   └── note_builder.py     # Markdown note + chart generation
├── notes/                  # Generated notes, one per day (archived)
├── charts/                 # Charts associated with each note
├── requirements.txt
└── README.md
```

## Installation

```bash
git clone <repo-url>
cd market-notes
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python3 src/note_builder.py
```

Automatically generates:
- A dated note in `notes/YYYY-MM-DD.md`
- An associated chart in `charts/YYYY-MM-DD.png`

The note includes a quick summary ("At a glance"), a focus section on notable moves (±1.5% threshold), a full breakdown of the calculations (collapsible), 
and two manually completed sections: an explanation of the day's move, and a short-term view — the part that reflects actual market judgment, deliberately 
left unautomated.

## Methodology and technical choices

- **Data window (3 months)**: the volatility (20-day rolling window) and correlation (30-day rolling window) indicators need enough history to be statistically
  stable. 3 months offers a balance between statistical stability and responsiveness to recent conditions - a deliberate, adjustable choice depending on intended use.
- **Base-100 normalization**: each instrument is indexed to its first *valid* value (not systematically the first row of the table), to avoid a missing early data
  point making an entire instrument disappear from the chart.
- **Notable move threshold (±1.5%)**: currently a fixed threshold applied uniformly to all instruments. A future improvement would be to make it relative to each
  asset's own volatility.

## Known limitations

- **Futures contract roll**: the `GC=F` (gold) and `CL=F` (oil) tickers can show occasional price jumps linked to the monthly contract rollover, not representative of
  an actual market move. Interpret long-term trend charts with caution.
- **Data source**: Yahoo Finance, so subject to occasional latency or data gaps, unlike a professional terminal (Bloomberg/Refinitiv).
- **Short-window correlations (30 days)**: should be read as a snapshot rather than a stable structural relationship over time.
