"""
Data quality checks and cleaning.
Every issue found is counted and written to reports/data_quality_report.md
so the cleaning is transparent and repeatable.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw_claims.csv"
CLEAN = ROOT / "data" / "clean_claims.csv"
REPORT = ROOT / "reports" / "data_quality_report.md"
PERIOD_END = pd.Timestamp("2026-06-30")


def main():
    df = pd.read_csv(RAW, keep_default_na=True)
    log = [("Rows received", len(df))]

    dups = df.duplicated(subset="claim_id", keep="first")
    log.append(("Duplicate claim IDs removed", int(dups.sum())))
    df = df[~dups].copy()

    bad_case = df["store"] != df["store"].str.title()
    log.append(("Store names with wrong capitalization fixed", int(bad_case.sum())))
    df["store"] = df["store"].str.title()

    missing_payer = df["payer"].isna()
    log.append(("Rows with missing payer (labelled 'Unknown')", int(missing_payer.sum())))
    df.loc[missing_payer, "payer"] = "Unknown"

    neg = df["claim_amount"] < 0
    log.append(("Negative claim amounts corrected (sign error)", int(neg.sum())))
    df.loc[neg, "claim_amount"] = df.loc[neg, "claim_amount"].abs()

    df["claim_date"] = pd.to_datetime(df["claim_date"], errors="coerce")
    future = df["claim_date"] > PERIOD_END
    log.append(("Rows with future dates removed", int(future.sum())))
    df = df[~future]

    log.append(("Rows after cleaning", len(df)))
    df.to_csv(CLEAN, index=False, date_format="%Y-%m-%d")

    lines = ["# Data Quality Report", "", "| Check | Result |", "|---|---|"]
    lines += [f"| {k} | {v:,} |" for k, v in log]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for k, v in log:
        print(f"{k}: {v:,}")


if __name__ == "__main__":
    main()
