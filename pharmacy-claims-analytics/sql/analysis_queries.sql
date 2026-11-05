-- name: kpis
SELECT COUNT(*)                                                  AS total_claims,
       ROUND(100.0 * SUM(status = 'Rejected') / COUNT(*), 2)     AS rejection_rate_pct,
       ROUND(100.0 * SUM(resubmitted_paid = 'Y') / NULLIF(SUM(status = 'Rejected'), 0), 1) AS recovery_rate_pct,
       ROUND(AVG(CASE WHEN resubmitted_paid = 'Y' THEN days_to_resolve END), 2) AS avg_days_to_resolve,
       ROUND(SUM(CASE WHEN status = 'Rejected' AND resubmitted_paid = 'N' THEN claim_amount ELSE 0 END), 2) AS unrecovered_amount
FROM claims;

-- name: monthly_trend
SELECT strftime('%Y-%m', claim_date)                             AS month,
       COUNT(*)                                                  AS claims,
       ROUND(100.0 * SUM(status = 'Rejected') / COUNT(*), 2)     AS rejection_rate_pct
FROM claims
GROUP BY month
ORDER BY month;

-- name: rejection_by_payer
SELECT payer,
       COUNT(*)                                                  AS claims,
       SUM(status = 'Rejected')                                  AS rejected,
       ROUND(100.0 * SUM(status = 'Rejected') / COUNT(*), 2)     AS rejection_rate_pct
FROM claims
WHERE payer <> 'Unknown'
GROUP BY payer
ORDER BY rejection_rate_pct DESC;

-- name: top_reject_reasons
SELECT c.reject_code,
       r.description,
       COUNT(*)                                                  AS rejections,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)        AS share_pct,
       ROUND(AVG(c.days_to_resolve), 2)                          AS avg_days_to_resolve
FROM claims c
JOIN reject_codes r ON r.reject_code = c.reject_code
WHERE c.status = 'Rejected'
GROUP BY c.reject_code, r.description
ORDER BY rejections DESC;

-- name: rejection_by_shift
SELECT shift,
       COUNT(*)                                                  AS claims,
       ROUND(100.0 * SUM(status = 'Rejected') / COUNT(*), 2)     AS rejection_rate_pct
FROM claims
GROUP BY shift
ORDER BY CASE shift WHEN 'Morning' THEN 1 WHEN 'Afternoon' THEN 2 ELSE 3 END;

-- name: store_scorecard
SELECT store,
       COUNT(*)                                                  AS claims,
       ROUND(100.0 * SUM(status = 'Rejected') / COUNT(*), 2)     AS rejection_rate_pct,
       ROUND(100.0 * SUM(resubmitted_paid = 'Y') / NULLIF(SUM(status = 'Rejected'), 0), 1) AS recovery_rate_pct
FROM claims
GROUP BY store
ORDER BY rejection_rate_pct DESC;
