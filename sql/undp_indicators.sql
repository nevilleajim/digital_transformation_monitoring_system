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
VALUES (
    'UNDP.HDI',
    'Human Development Index',
    'Human Development',
    'Composite index measuring average achievement in health, education, and standard of living.',
    'Index, 0 to 1',
    (
        SELECT id
        FROM data_sources
        WHERE source_name = 'United Nations Development Programme'
        ORDER BY id
        LIMIT 1
    ),
    'Annual',
    'Essential'
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
