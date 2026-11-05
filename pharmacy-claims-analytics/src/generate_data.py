"""
Generates a realistic but fully synthetic dataset of pharmacy insurance claims
(January to June 2026). No real patients, pharmacies or insurer data are used.

A few data quality problems are added on purpose (duplicates, missing values,
negative amounts, bad dates) so the cleaning step has real work to do.
"""
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
OUT = Path(__file__).resolve().parents[1] / "data" / "raw_claims.csv"

PAYERS = {               # payer: (share of claims, base rejection rate)
    "Public Drug Plan": (0.42, 0.06),
    "Private Plan A":   (0.18, 0.08),
    "Private Plan B":   (0.14, 0.11),
    "Private Plan C":   (0.12, 0.07),
    "Private Plan D":   (0.09, 0.15),
    "Private Plan E":   (0.05, 0.09),
}
REJECT_CODES = {         # code: (description, relative frequency, avg days to resolve)
    "R01": ("Refill too soon", 0.30, 0.5),
    "R02": ("Patient not eligible / coverage ended", 0.18, 3.0),
    "R03": ("Drug not covered by plan", 0.16, 4.0),
    "R04": ("Prior authorization required", 0.12, 6.0),
    "R05": ("Invalid patient ID or date of birth", 0.11, 1.0),
    "R06": ("Quantity or days supply exceeds limit", 0.08, 1.5),
    "R07": ("Invalid prescriber ID", 0.05, 2.0),
}
DRUG_CLASSES = ["Cardiovascular", "Diabetes", "Mental Health", "Respiratory",
                "Pain Management", "Antibiotics", "Cholesterol", "Thyroid"]
STORES = ["Store 1 - Downtown", "Store 2 - East End", "Store 3 - South", "Store 4 - West"]
SHIFTS = ["Morning", "Afternoon", "Evening"]


def main(n_claims=24000):
    payer_names = list(PAYERS)
    payer_share = np.array([PAYERS[p][0] for p in payer_names])
    dates = pd.to_datetime("2026-01-01") + pd.to_timedelta(RNG.integers(0, 181, n_claims), unit="D")

    df = pd.DataFrame({
        "claim_id": [f"CLM{100000 + i}" for i in range(n_claims)],
        "claim_date": dates,
        "store": RNG.choice(STORES, n_claims, p=[0.35, 0.25, 0.22, 0.18]),
        "shift": RNG.choice(SHIFTS, n_claims, p=[0.40, 0.38, 0.22]),
        "payer": RNG.choice(payer_names, n_claims, p=payer_share / payer_share.sum()),
        "drug_class": RNG.choice(DRUG_CLASSES, n_claims),
        "patient_age_band": RNG.choice(["0-17", "18-39", "40-64", "65+"], n_claims, p=[0.08, 0.22, 0.35, 0.35]),
        "claim_amount": np.round(RNG.lognormal(mean=3.6, sigma=0.8, size=n_claims), 2),
    })

    # Rejection probability: payer base rate, higher on evenings and in January (plan renewals)
    base = df["payer"].map({p: v[1] for p, v in PAYERS.items()})
    prob = base * np.where(df["shift"] == "Evening", 1.35, 1.0) * np.where(df["claim_date"].dt.month == 1, 1.4, 1.0)
    rejected = RNG.random(n_claims) < prob

    codes = list(REJECT_CODES)
    code_p = np.array([REJECT_CODES[c][1] for c in codes])
    df["status"] = np.where(rejected, "Rejected", "Paid")
    df["reject_code"] = np.where(rejected, RNG.choice(codes, n_claims, p=code_p / code_p.sum()), "")

    # Resolution of rejected claims
    resolved = rejected & (RNG.random(n_claims) < 0.82)
    avg_days = df["reject_code"].map({c: v[2] for c, v in REJECT_CODES.items()}).fillna(0)
    df["resubmitted_paid"] = np.where(resolved, "Y", np.where(rejected, "N", ""))
    df["days_to_resolve"] = np.where(resolved, np.round(RNG.exponential(avg_days.clip(lower=0.2)), 1), np.nan)

    # Inject data quality problems on purpose
    dup = df.sample(60, random_state=1)
    df = pd.concat([df, dup], ignore_index=True)
    df.loc[df.sample(45, random_state=2).index, "payer"] = None
    df.loc[df.sample(20, random_state=3).index, "claim_amount"] *= -1
    df.loc[df.sample(12, random_state=4).index, "claim_date"] = pd.Timestamp("2027-03-15")
    idx = df.sample(25, random_state=5).index
    df.loc[idx, "store"] = df.loc[idx, "store"].str.upper()

    df["claim_date"] = df["claim_date"].dt.strftime("%Y-%m-%d")
    df = df.sample(frac=1, random_state=7).reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df):,} rows to data/{OUT.name}")

    codes_df = pd.DataFrame([(c, d) for c, (d, _, _) in REJECT_CODES.items()],
                            columns=["reject_code", "description"])
    codes_df.to_csv(OUT.parent / "reject_codes.csv", index=False)


if __name__ == "__main__":
    main()
