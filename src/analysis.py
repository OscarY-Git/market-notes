import pandas as pd

def compute_returns(df: pd.DataFrame, horizons: dict = None) -> pd.DataFrame:
    """
    Calcule la variation en % sur plusieurs horizons (1j, 1sem, 1mois).
    Retourne un tableau récapitulatif (une ligne par instrument).
    """
    if horizons is None:
        horizons = {"1D": 1, "1W": 5, "1M": 21}  # en jours de trading

    results = {}
    for label, n_days in horizons.items():
        if len(df) > n_days:
            pct_change = (df.iloc[-1] / df.iloc[-1 - n_days] - 1) * 100
            results[label] = pct_change.round(2)

    return pd.DataFrame(results)

def compute_volatility(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """
    Calcule la volatilité annualisée (écart-type des rendements quotidiens)
    sur une fenêtre glissante, pour le dernier jour disponible.
    """
    daily_returns = df.pct_change()
    rolling_vol = daily_returns.rolling(window=window).std() * (252 ** 0.5) * 100
    return rolling_vol.iloc[-1].round(2)

def compute_correlations(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Calcule la matrice de corrélation entre instruments
    sur les 'window' derniers jours.
    """
    daily_returns = df.pct_change().tail(window)
    return daily_returns.corr().round(2)

def flag_notable_moves(returns_1d: pd.Series, threshold: float = 1.5) -> pd.Series:
    """
    Identifie les instruments dont la variation du jour dépasse un seuil,
    donc qui méritent une explication dans la note.
    """
    return returns_1d[returns_1d.abs() >= threshold]

if __name__ == "__main__":
    from data_fetch import fetch_data, CORE_TICKERS

    df = fetch_data(CORE_TICKERS, period="3mo")  # 3 mois pour avoir assez d'historique

    print("=== Rendements multi-horizons ===")
    returns = compute_returns(df)
    print(returns)

    print("\n=== Volatilité annualisée (%) ===")
    vol = compute_volatility(df)
    print(vol)

    print("\n=== Corrélations (30 derniers jours) ===")
    corr = compute_correlations(df)
    print(corr)

    print("\n=== Mouvements notables du jour (>1.5%) ===")
    notable = flag_notable_moves(returns["1D"])
    print(notable if not notable.empty else "Aucun mouvement notable aujourd'hui")