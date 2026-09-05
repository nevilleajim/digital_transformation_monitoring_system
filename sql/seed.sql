INSERT INTO data_sources (source_name, source_url)
VALUES
    (
        'World Bank',
        'https://data.worldbank.org/'
    ),
    (
        'International Telecommunication Union',
        'https://datahub.itu.int/'
    ),
    (
        'United Nations DESA',
        'https://publicadministration.un.org/egovkb/'
    ),
    (
        'United Nations Development Programme',
        'https://hdr.undp.org/data-center'
    );


INSERT INTO countries (country_code, country_name, region)
VALUES
    ('CMR', 'Cameroon', 'Sub-Saharan Africa'),
    ('GHA', 'Ghana', 'Sub-Saharan Africa'),
    ('KEN', 'Kenya', 'Sub-Saharan Africa'),
    ('NGA', 'Nigeria', 'Sub-Saharan Africa'),
    ('RWA', 'Rwanda', 'Sub-Saharan Africa'),
    ('ZAF', 'South Africa', 'Sub-Saharan Africa');


INSERT INTO indicators
(
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
    'IT.NET.USER.ZS',
    'Individuals using the Internet',
    'Digital Access',
    'Individuals who have used the Internet from any location in the last three months.',
    'Percentage of population',
    1,
    'Annual',
    'Essential'
),

(
    'IT.CEL.SETS.P2',
    'Mobile cellular subscriptions',
    'Digital Access',
    'Mobile cellular telephone subscriptions per 100 people.',
    'Per 100 people',
    1,
    'Annual',
    'Essential'
),

(
    'IT.NET.BBND.P2',
    'Fixed broadband subscriptions',
    'Digital Access',
    'Fixed broadband subscriptions per 100 people.',
    'Per 100 people',
    1,
    'Annual',
    'Essential'
),

(
    'EG.ELC.ACCS.ZS',
    'Access to electricity',
    'Digital Access',
    'Percentage of the population with access to electricity.',
    'Percentage of population',
    1,
    'Annual',
    'Important'
),

(
    'NY.GDP.PCAP.CD',
    'GDP per capita',
    'Context',
    'Gross domestic product divided by midyear population.',
    'Current US dollars',
    1,
    'Annual',
    'Important'
);