-- SQLite schema for cleaned pharmacy claims
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS reject_codes;

CREATE TABLE reject_codes (
    reject_code  TEXT PRIMARY KEY,
    description  TEXT NOT NULL
);

CREATE TABLE claims (
    claim_id          TEXT PRIMARY KEY,
    claim_date        DATE NOT NULL,
    store             TEXT NOT NULL,
    shift             TEXT NOT NULL,
    payer             TEXT NOT NULL,
    drug_class        TEXT NOT NULL,
    patient_age_band  TEXT,
    claim_amount      REAL NOT NULL CHECK (claim_amount >= 0),
    status            TEXT NOT NULL CHECK (status IN ('Paid', 'Rejected')),
    reject_code       TEXT REFERENCES reject_codes(reject_code),
    resubmitted_paid  TEXT,
    days_to_resolve   REAL
);

CREATE INDEX idx_claims_date  ON claims (claim_date);
CREATE INDEX idx_claims_payer ON claims (payer, status);
