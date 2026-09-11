-- 1. Total number of observations
SELECT COUNT(*) AS total_observations
FROM indicator_values;


-- 2. Number of observations by country
SELECT
    c.country_name,
    COUNT(*) AS observations
FROM indicator_values iv
JOIN countries c
    ON iv.country_id = c.id
GROUP BY c.country_name
ORDER BY observations DESC;


-- 3. Number of observations by indicator
SELECT
    i.indicator_name,
    COUNT(*) AS observations
FROM indicator_values iv
JOIN indicators i
    ON iv.indicator_id = i.id
GROUP BY i.indicator_name
ORDER BY observations DESC;


-- 4. Available years
SELECT
    MIN(year) AS earliest_year,
    MAX(year) AS latest_year
FROM indicator_values;


-- 5. Average value by country and indicator
SELECT
    c.country_name,
    i.indicator_name,
    ROUND(AVG(iv.value), 2) AS average_value
FROM indicator_values iv
JOIN countries c
    ON iv.country_id = c.id
JOIN indicators i
    ON iv.indicator_id = i.id
GROUP BY
    c.country_name,
    i.indicator_name
ORDER BY
    c.country_name,
    i.indicator_name;


-- 6. Latest available value for every country/indicator
SELECT DISTINCT ON (
    c.country_name,
    i.indicator_code
)
    c.country_name,
    i.indicator_name,
    iv.year,
    iv.value,
    i.unit
FROM indicator_values iv
JOIN countries c
    ON iv.country_id = c.id
JOIN indicators i
    ON iv.indicator_id = i.id
ORDER BY
    c.country_name,
    i.indicator_code,
    iv.year DESC;


-- 7. Yearly average across countries
SELECT
    iv.year,
    i.indicator_name,
    ROUND(AVG(iv.value), 2) AS average_value
FROM indicator_values iv
JOIN indicators i
    ON iv.indicator_id = i.id
GROUP BY
    iv.year,
    i.indicator_name
ORDER BY
    iv.year,
    i.indicator_name;


-- 8. Minimum and maximum values
SELECT
    c.country_name,
    i.indicator_name,
    MIN(iv.value) AS minimum_value,
    MAX(iv.value) AS maximum_value
FROM indicator_values iv
JOIN countries c
    ON iv.country_id = c.id
JOIN indicators i
    ON iv.indicator_id = i.id
GROUP BY
    c.country_name,
    i.indicator_name
ORDER BY
    c.country_name,
    i.indicator_name;

-- Year-over-year change
SELECT
    c.country_name,
    i.indicator_name,
    iv.year,
    iv.value,

    LAG(iv.value) OVER (
        PARTITION BY
            iv.country_id,
            iv.indicator_id
        ORDER BY iv.year
    ) AS previous_value,

    iv.value -
    LAG(iv.value) OVER (
        PARTITION BY
            iv.country_id,
            iv.indicator_id
        ORDER BY iv.year
    ) AS absolute_change

FROM indicator_values iv
JOIN countries c
    ON iv.country_id = c.id
JOIN indicators i
    ON iv.indicator_id = i.id

ORDER BY
    c.country_name,
    i.indicator_name,
    iv.year;