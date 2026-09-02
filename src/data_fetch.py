import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Ton socle d'instruments (cross-asset)
CORE_TICKERS = {
    "US 10Y Yield": "^TNX",
    "EUR/USD": "EURUSD=X",
    "S&P 500": "^GSPC",
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
}

def fetch_data(tickers: dict, period: str = "1mo") -> pd.DataFrame:
    """
    Récupère les données de prix pour un dictionnaire {nom: ticker}.
    Retourne un DataFrame avec un prix de clôture par jour calendaire.
    """
    data = {}
    for name, ticker in tickers.items():
        try:
            hist = yf.Ticker(ticker).history(period=period)
            if not hist.empty:
                # On retire le fuseau horaire pour comparer uniquement les dates
                hist.index = hist.index.tz_localize(None).normalize()
                series = hist["Close"]
                # S'il reste des doublons sur une même date, on garde la dernière valeur
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
    """
    Récupère les données pour un instrument "focus" ponctuel
    (ex: une action spécifique qui t'intéresse ce jour-là).
    """
    hist = yf.Ticker(ticker).history(period=period)
    return hist["Close"] if not hist.empty else None

def compute_daily_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule la variation en % sur le dernier jour disponible.
    """
    changes = df.pct_change().iloc[-1] * 100
    return changes.round(2)

if __name__ == "__main__":
    # Test rapide du script
    df = fetch_data(CORE_TICKERS)
    print("Dernières valeurs :")
    print(df.tail())
    print("\nVariations du jour (%) :")
    print(compute_daily_changes(df))