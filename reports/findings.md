# Findings: Pharmacy Claims Rejection Analysis (Jan–Jun 2026)

## Headline KPIs

| Metric | Value |
|---|---|
| Claims analyzed | 23,988 |
| Rejection rate | 9.57% |
| Rejected claims recovered after resubmission | 81.9% |
| Average days to resolve a rejection | 2.48 |
| Unrecovered claim value | $20,532.12 |

## Key insights

1. **A few reasons drive most rejections.** "Refill too soon" is the top reason (30.0% of rejections), and the top three reasons together make up 63.2%.
2. **Payer matters.** Private Plan D rejects 17.98% of claims, versus 6.85% for Public Drug Plan.
3. **Evening shift has a higher rejection rate** (11.51% vs 8.93% in the morning), suggesting less time for eligibility checks.
4. **January spike.** Rejections were 12.64% in January versus an average of 8.9% in later months, consistent with plan renewals and coverage changes at the start of the year.

## Recommendations

- Check refill dates before submitting, to cut "refill too soon" rejections.
- Verify coverage and patient ID at intake, especially in January when plans change.
- Keep a quick-reference sheet of prior authorization rules for the highest-rejecting payers.
- Add an eligibility checklist or extra support for the evening shift.

## Supporting tables

### Rejection by payer
| payer | claims | rejected | rejection_rate_pct |
|---|---|---|---|
| Private Plan D | 2152 | 387 | 17.98 |
| Private Plan B | 3386 | 453 | 13.38 |
| Private Plan E | 1217 | 131 | 10.76 |
| Private Plan C | 2828 | 252 | 8.91 |
| Private Plan A | 4504 | 395 | 8.77 |
| Public Drug Plan | 9856 | 675 | 6.85 |

### Top rejection reasons
| reject_code | description | rejections | share_pct | avg_days_to_resolve |
|---|---|---|---|---|
| R01 | Refill too soon | 688 | 30.0 | 0.5 |
| R02 | Patient not eligible / coverage ended | 420 | 18.3 | 3.11 |
| R03 | Drug not covered by plan | 341 | 14.9 | 4.4 |
| R04 | Prior authorization required | 284 | 12.4 | 6.29 |
| R05 | Invalid patient ID or date of birth | 266 | 11.6 | 0.95 |
| R06 | Quantity or days supply exceeds limit | 176 | 7.7 | 1.5 |
| R07 | Invalid prescriber ID | 120 | 5.2 | 1.99 |

### Store scorecard
| store | claims | rejection_rate_pct | recovery_rate_pct |
|---|---|---|---|
| Store 1 - Downtown | 8372 | 9.83 | 83.2 |
| Store 4 - West | 4312 | 9.55 | 82.3 |
| Store 3 - South | 5425 | 9.42 | 80.8 |
| Store 2 - East End | 5879 | 9.34 | 80.5 |
