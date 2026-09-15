WITH source AS (
    SELECT id
    FROM data_sources
    WHERE source_name = 'International Telecommunication Union'
    ORDER BY id
    LIMIT 1
)
INSERT INTO indicators (
    indicator_code,
    indicator_name,
    dimension,
    definition,
    unit,
    source_id,
    frequency,
    priority
)
VALUES
(
    'ITU.IT_NET_USER',
    'Individuals using the Internet',
    'Digital Access',
    'Percentage of individuals using the Internet.',
    'Percentage of population',
    (SELECT id FROM source),
    'Annual',
    'Essential'
),
(
    'ITU.IT_CEL_SETS_P2',
    'Mobile cellular subscriptions',
    'Digital Access',
    'Mobile cellular subscriptions per 100 people.',
    'Per 100 people',
    (SELECT id FROM source),
    'Annual',
    'Essential'
),
(
    'ITU.IT_NET_BBND_P2',
    'Fixed broadband subscriptions',
    'Digital Access',
    'Fixed broadband subscriptions per 100 people.',
    'Per 100 people',
    (SELECT id FROM source),
    'Annual',
    'Essential'
),
(
    'ITU.IT_MLT_MAIN_P2',
    'Fixed telephone subscriptions',
    'Digital Access',
    'Fixed telephone subscriptions per 100 people.',
    'Per 100 people',
    (SELECT id FROM source),
    'Annual',
    'Important'
),
(
    'ITU.IT_NET_USER_M',
    'Male individuals using the Internet',
    'Digital Inclusion',
    'Percentage of male individuals using the Internet.',
    'Percentage of male population',
    (SELECT id FROM source),
    'Annual',
    'Important'
),
(
    'ITU.IT_NET_USER_F',
    'Female individuals using the Internet',
    'Digital Inclusion',
    'Percentage of female individuals using the Internet.',
    'Percentage of female population',
    (SELECT id FROM source),
    'Annual',
    'Important'
)
ON CONFLICT (indicator_code)
DO UPDATE SET
    indicator_name = EXCLUDED.indicator_name,
    dimension = EXCLUDED.dimension,
    definition = EXCLUDED.definition,
    unit = EXCLUDED.unit,
    source_id = EXCLUDED.source_id,
    frequency = EXCLUDED.frequency,
    priority = EXCLUDED.priority;
