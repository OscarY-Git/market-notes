import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import date

from data_fetch import fetch_data, CORE_TICKERS
from analysis import compute_returns, compute_volatility, compute_correlations, flag_notable_moves


# --- Emojis pour visualiser rapidement le sens du mouvement ---
def move_emoji(pct: float) -> str:
    if pct >= 1.5:
        return "🟢"
    elif pct <= -1.5:
        return "🔴"
    else:
        return "⚪"


def generate_chart(df: pd.DataFrame, save_path: str):
    """
    Génère un graphique en 2 panels :
    - évolution des prix normalisés (base 100) sur la période
    - variations du jour en histogramme
    """
    first_valid = df.apply(lambda col: col.dropna().iloc[0])
    normalized = df / first_valid * 100
    daily_change = df.pct_change().iloc[-1] * 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # Panel 1 : évolution normalisée
    for col in normalized.columns:
        axes[0].plot(normalized.index, normalized[col], label=col)
    axes[0].set_title("Évolution (base 100)")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    # Gestion propre des dates sur l'axe X
    axes[0].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))  # 1 label toutes les 2 semaines
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))    # format "21 Aug"
    axes[0].tick_params(axis="x", rotation=45)

    # Panel 2 : variations du jour
    colors = ["green" if v >= 0 else "red" for v in daily_change]
    axes[1].bar(daily_change.index, daily_change.values, color=colors)
    axes[1].set_title("Variation du jour (%)")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=120)
    plt.close()


def build_note(df: pd.DataFrame, chart_path: str, note_date: str) -> str:
    """
    Assemble la note markdown complète.
    """
    returns = compute_returns(df)
    vol = compute_volatility(df)
    corr = compute_correlations(df)
    notable = flag_notable_moves(returns["1D"])

    lines = [f"# Market Note — {note_date}\n"]

    # --- Section "En bref" ---
    lines.append("## 🔑 En bref")
    for instrument in returns.index:
        pct = returns.loc[instrument, "1D"]
        lines.append(f"- {move_emoji(pct)} {instrument} {pct:+.2f}%")
    lines.append("")

    # --- Graphique ---
    chart_filename = os.path.basename(chart_path)
    lines.append("## 📊 Graphique du jour")
    lines.append(f"![chart](../charts/{chart_filename})\n")

    # --- Focus mouvements notables ---
    lines.append("## 🔍 Focus : mouvement(s) notable(s)")
    if notable.empty:
        lines.append("Aucun mouvement notable aujourd'hui (seuil : ±1.5%).\n")
    else:
        for instrument, pct in notable.items():
            lines.append(f"**{instrument} ({pct:+.2f}%)** — _[à compléter : explication]_\n")

    # --- Détails techniques repliables ---
    lines.append("<details>")
    lines.append("<summary>📈 Voir le détail complet (multi-horizons, vol, corrélations)</summary>\n")

    lines.append("### Rendements multi-horizons (%)")
    lines.append(returns.to_markdown())
    lines.append("")

    lines.append("### Volatilité annualisée (%)")
    lines.append(vol.to_frame(name="Vol annualisée").to_markdown())
    lines.append("")

    lines.append("### Corrélations (30 derniers jours)")
    lines.append(corr.to_markdown())
    lines.append("\n</details>\n")

    # --- Vue ---
    lines.append("## 🎯 Vue")
    lines.append("_[à compléter : ta vue à 1-2 semaines]_\n")

    # --- Suivi vue précédente ---
    lines.append("## ✅ Suivi de la vue précédente")
    lines.append("_[à compléter manuellement, ou automatisé plus tard]_\n")

    return "\n".join(lines)


if __name__ == "__main__":
    today = date.today().isoformat()

    df = fetch_data(CORE_TICKERS, period="3mo")

    chart_path = f"charts/{today}.png"
    generate_chart(df, chart_path)

    note_content = build_note(df, chart_path, today)

    note_path = f"notes/{today}.md"
    with open(note_path, "w") as f:
        f.write(note_content)

    print(f"✅ Note générée : {note_path}")
    print(f"✅ Graphique généré : {chart_path}")