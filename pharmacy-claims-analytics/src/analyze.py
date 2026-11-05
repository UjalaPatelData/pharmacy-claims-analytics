"""
Loads the cleaned claims into SQLite, runs the SQL analysis queries,
saves charts to reports/figures and writes reports/findings.md.
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "claims.db"
FIG = ROOT / "reports" / "figures"
BLUE, ORANGE, GREY = "#1F4E79", "#E07B39", "#9AA5B1"


def load_queries():
    text = (ROOT / "sql" / "analysis_queries.sql").read_text(encoding="utf-8")
    queries, name = {}, None
    for line in text.splitlines():
        if line.startswith("-- name:"):
            name = line.split(":", 1)[1].strip()
            queries[name] = ""
        elif name:
            queries[name] += line + "\n"
    return queries


def build_db():
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
    pd.read_csv(ROOT / "data" / "reject_codes.csv").to_sql("reject_codes", con, if_exists="append", index=False)
    claims = pd.read_csv(ROOT / "data" / "clean_claims.csv")
    claims["reject_code"] = claims["reject_code"].astype(object).where(claims["reject_code"].notna(), None)
    claims.to_sql("claims", con, if_exists="append", index=False)
    return con


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold", color="#222")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def md_table(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(out)


def main():
    con = build_db()
    r = {name: pd.read_sql_query(sql, con) for name, sql in load_queries().items()}
    FIG.mkdir(parents=True, exist_ok=True)

    m = r["monthly_trend"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(m["month"], m["rejection_rate_pct"], marker="o", color=BLUE, linewidth=2)
    for x, y in zip(m["month"], m["rejection_rate_pct"]):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax.set_ylabel("Rejection rate (%)")
    ax.set_ylim(0, m["rejection_rate_pct"].max() * 1.25)
    style(ax, "Monthly claim rejection rate")
    fig.tight_layout(); fig.savefig(FIG / "01_monthly_rejection_rate.png", dpi=150); plt.close(fig)

    p = r["rejection_by_payer"]
    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [ORANGE if v == p["rejection_rate_pct"].max() else BLUE for v in p["rejection_rate_pct"]]
    ax.barh(p["payer"][::-1], p["rejection_rate_pct"][::-1], color=colors[::-1])
    ax.set_xlabel("Rejection rate (%)")
    style(ax, "Rejection rate by payer")
    ax.grid(axis="x", alpha=0.25); ax.grid(axis="y", visible=False)
    fig.tight_layout(); fig.savefig(FIG / "02_rejection_by_payer.png", dpi=150); plt.close(fig)

    t = r["top_reject_reasons"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(t["description"], t["rejections"], color=BLUE)
    ax2 = ax.twinx()
    ax2.plot(t["description"], t["share_pct"].cumsum(), color=ORANGE, marker="o")
    ax2.set_ylim(0, 105); ax2.set_ylabel("Cumulative share (%)")
    ax.set_ylabel("Rejected claims")
    ax.tick_params(axis="x", rotation=30, labelsize=8)
    plt.setp(ax.get_xticklabels(), ha="right")
    style(ax, "Top rejection reasons (Pareto)")
    fig.tight_layout(); fig.savefig(FIG / "03_top_reject_reasons.png", dpi=150); plt.close(fig)

    s = r["rejection_by_shift"]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(s["shift"], s["rejection_rate_pct"], color=[GREY, GREY, ORANGE])
    for i, v in enumerate(s["rejection_rate_pct"]):
        ax.text(i, v + 0.15, f"{v:.1f}%", ha="center", fontsize=10)
    ax.set_ylabel("Rejection rate (%)")
    style(ax, "Rejection rate by shift")
    fig.tight_layout(); fig.savefig(FIG / "04_rejection_by_shift.png", dpi=150); plt.close(fig)

    k = r["kpis"].iloc[0]
    top = t.iloc[0]
    top3 = t["share_pct"].head(3).sum()
    worst, best = p.iloc[0], p.iloc[-1]
    sh = s.set_index("shift")["rejection_rate_pct"]
    jan, later = m.iloc[0]["rejection_rate_pct"], m.iloc[1:]["rejection_rate_pct"].mean()

    findings = f"""# Findings: Pharmacy Claims Rejection Analysis (Jan–Jun 2026)

## Headline KPIs

| Metric | Value |
|---|---|
| Claims analyzed | {int(k.total_claims):,} |
| Rejection rate | {k.rejection_rate_pct}% |
| Rejected claims recovered after resubmission | {k.recovery_rate_pct}% |
| Average days to resolve a rejection | {k.avg_days_to_resolve} |
| Unrecovered claim value | ${k.unrecovered_amount:,.2f} |

## Key insights

1. **A few reasons drive most rejections.** "{top.description}" is the top reason ({top.share_pct}% of rejections), and the top three reasons together make up {top3:.1f}%.
2. **Payer matters.** {worst.payer} rejects {worst.rejection_rate_pct}% of claims, versus {best.rejection_rate_pct}% for {best.payer}.
3. **Evening shift has a higher rejection rate** ({sh['Evening']}% vs {sh['Morning']}% in the morning), suggesting less time for eligibility checks.
4. **January spike.** Rejections were {jan}% in January versus an average of {later:.1f}% in later months, consistent with plan renewals and coverage changes at the start of the year.

## Recommendations

- Check refill dates before submitting, to cut "refill too soon" rejections.
- Verify coverage and patient ID at intake, especially in January when plans change.
- Keep a quick-reference sheet of prior authorization rules for the highest-rejecting payers.
- Add an eligibility checklist or extra support for the evening shift.

## Supporting tables

### Rejection by payer
{md_table(p)}

### Top rejection reasons
{md_table(t)}

### Store scorecard
{md_table(r["store_scorecard"])}
"""
    (ROOT / "reports" / "findings.md").write_text(findings, encoding="utf-8")
    con.close()
    print("Charts saved to reports/figures; findings saved to reports/findings.md")


if __name__ == "__main__":
    main()
