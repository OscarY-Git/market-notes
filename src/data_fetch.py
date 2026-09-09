import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

CORE_TICKERS = {
    "US 10Y Yield": "^TNX",
    "EUR/USD": "EURUSD=X",
    "S&P 500": "^GSPC",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
}

def fetch_data(tickers: dict, period: str = "1mo") -> pd.DataFrame:
    data = {}
    for name, ticker in tickers.items():
        try:
            hist = yf.Ticker(ticker).history(period=period)
            if not hist.empty:
                hist.index = hist.index.tz_localize(None).normalize()
                series = hist["Close"]
                series = series.groupby(series.index).last()
                data[name] = series
            else:
                print(f"⚠️ Pas de données pour {name} ({ticker})")
        except Exception as e:
            print(f"❌ Erreur pour {name} ({ticker}): {e}")

    df = pd.DataFrame(data)
    df = df.sort_index()
    df = df.ffill()
    return df

def fetch_focus(ticker: str, period: str = "1mo") -> pd.Series:
    hist = yf.Ticker(ticker).history(period=period)
    return hist["Close"] if not hist.empty else None

def compute_daily_changes(df: pd.DataFrame) -> pd.DataFrame:
    changes = df.pct_change().iloc[-1] * 100
    return changes.round(2)

if __name__ == "__main__":
    df = fetch_data(CORE_TICKERS)
    print("Dernières valeurs :")
    print(df.tail())
    print("\nVariations du jour (%) :")
    print(compute_daily_changes(df))