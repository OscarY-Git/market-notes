import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import date

from data_fetch import fetch_data, CORE_TICKERS
from analysis import (
    compute_returns,
    compute_volatility,
    compute_correlations,
    flag_notable_moves,
)


def move_emoji(pct: float) -> str:
    if pct >= 1.5:
        return "🟢"
    elif pct <= -1.5:
        return "🔴"
    else:
        return "⚪"


def generate_chart(df: pd.DataFrame, save_path: str):
    first_valid = df.apply(lambda col: col.dropna().iloc[0])
    normalized = df / first_valid * 100
    daily_change = df.pct_change().iloc[-1] * 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    for col in normalized.columns:
        axes[0].plot(normalized.index, normalized[col], label=col)
    axes[0].set_title("Performance (base 100)")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    axes[0].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    axes[0].tick_params(axis="x", rotation=45)

    colors = ["green" if v >= 0 else "red" for v in daily_change]
    axes[1].bar(daily_change.index, daily_change.values, color=colors)
    axes[1].set_title("Daily change (%)")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=120)
    plt.close()


def build_note(df: pd.DataFrame, chart_path: str, note_date: str) -> str:
    returns = compute_returns(df)
    vol = compute_volatility(df)
    corr = compute_correlations(df)
    notable = flag_notable_moves(returns["1D"])

    lines = [f"# Market Note — {note_date}\n"]

    # --- "At a glance" section ---
    lines.append("## 🔑 At a glance")
    for instrument in returns.index:
        pct = returns.loc[instrument, "1D"]
        lines.append(f"- {move_emoji(pct)} {instrument} {pct:+.2f}%")
    lines.append("")

    # --- Chart ---
    chart_filename = os.path.basename(chart_path)
    lines.append("## 📊 Chart")
    lines.append(f"![chart](../charts/{chart_filename})\n")

    # --- Focus on notable moves ---
    lines.append("## 🔍 Focus: notable move(s)")
    if notable.empty:
        lines.append("No notable move today (threshold: ±1.5%).\n")
    else:
        for instrument, pct in notable.items():
            lines.append(f"**{instrument} ({pct:+.2f}%)** — _[to complete: explanation]_\n")

    # --- Collapsible technical details ---
    lines.append("<details>")
    lines.append("<summary>📈 View full details (multi-horizon returns, volatility, correlations)</summary>\n")

    lines.append("### Multi-horizon returns (%)")
    lines.append(returns.to_markdown())
    lines.append("")

    lines.append("### Annualized volatility (%)")
    lines.append(vol.to_frame(name="Annualized vol").to_markdown())
    lines.append("")

    lines.append("### Correlations (last 30 days)")
    lines.append(corr.to_markdown())
    lines.append("\n</details>\n")

    # --- View ---
    lines.append("## 🎯 View")
    lines.append("_[to complete: your 1-2 week view]_\n")

    # --- Follow-up on previous view ---
    lines.append("## ✅ Follow-up on previous view")
    lines.append("_[to complete manually, or automate later]_\n")

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

    print(f"✅ Note generated: {note_path}")
    print(f"✅ Chart generated: {chart_path}")