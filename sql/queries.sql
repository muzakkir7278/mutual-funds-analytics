
-- 1. Top 5 funds by AUM
SELECT f.scheme_name, a.aum_crore
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
ORDER BY a.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT scheme_code, strftime('%Y-%m', date) AS month, AVG(nav) AS avg_nav
FROM fact_nav
GROUP BY scheme_code, strftime('%Y-%m', date);

-- 3. SIP transaction amount by state
SELECT state, SUM(amount) AS total_sip_amount
FROM fact_transactions
WHERE transaction_type = 'Sip'
GROUP BY state
ORDER BY total_sip_amount DESC;

-- 4. Funds with expense ratio below 1%
SELECT f.scheme_name, p.expense_ratio
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
WHERE p.expense_ratio < 1
ORDER BY p.expense_ratio;

-- 5. Top funds by one year return
SELECT f.scheme_name, p.one_year_return
FROM fact_performance p
JOIN dim_fund f ON p.scheme_code = f.scheme_code
ORDER BY p.one_year_return DESC
LIMIT 5;

-- 6. Category-wise fund count
SELECT category, COUNT(*) AS total_funds
FROM dim_fund
GROUP BY category;

-- 7. Risk grade-wise fund count
SELECT risk_grade, COUNT(*) AS total_funds
FROM dim_fund
GROUP BY risk_grade;

-- 8. Total transaction amount by transaction type
SELECT transaction_type, SUM(amount) AS total_amount
FROM fact_transactions
GROUP BY transaction_type;

-- 9. Category-wise AUM
SELECT f.category, SUM(a.aum_crore) AS total_aum
FROM fact_aum a
JOIN dim_fund f ON a.scheme_code = f.scheme_code
GROUP BY f.category
ORDER BY total_aum DESC;

-- 10. NAV trend by scheme
SELECT f.scheme_name, n.date, n.nav
FROM fact_nav n
JOIN dim_fund f ON n.scheme_code = f.scheme_code
ORDER BY f.scheme_name, n.date;
