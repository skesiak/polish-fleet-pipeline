WITH monthly AS (
    SELECT
        period, 
        fuel_category,
        SUM(registrations) AS registrations
    FROM fct_registrations_monthly
    GROUP BY period, fuel_category
)
SELECT
    period,
    fuel_category,
    registrations,
    SUM(registrations) OVER (PARTITION BY period) AS period_total,
    ROUND(registrations * 100.0 / SUM(registrations) OVER (PARTITION BY period), 1) AS share_pct,
    LAG(registrations) OVER (PARTITION BY fuel_category ORDER BY period) AS prev_registrations,
    ROUND((registrations - LAG(registrations) OVER (PARTITION BY fuel_category ORDER BY period)) * 100.0 / LAG(registrations) OVER (PARTITION BY fuel_category ORDER BY period), 1) AS mom_change_pct,
    LAG(registrations, 12) OVER (PARTITION BY fuel_category ORDER BY period) AS registrations_year_ago,
    ROUND((registrations - LAG(registrations, 12) OVER (PARTITION BY fuel_category ORDER BY period)) * 100.0 / LAG(registrations, 12) OVER (PARTITION BY fuel_category ORDER BY period), 1) AS yoy_change_pct
FROM monthly
ORDER BY fuel_category, period;