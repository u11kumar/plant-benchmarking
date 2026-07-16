import pandas as pd

# FY 2023-24 snapshot benchmarking table (9 plants) as compiled in analysis.md.
# Note: Anpara-A, Parichha Extn., and Obra-B are the 3 plants with full audited
# time-series data in Book2.xlsx; the remaining 6 are supplied here as reference
# benchmark values (from the prior benchmarking exercise) for wider peer comparison.
data = [
    # name, capacity_mw, units, plf, shr, apc, gcv, oil_ml_kwh, energy_mu, com_year, tech, in_workbook
    ('Jawaharpur', 1320, '2x660 MW', 85.0, 2049, 5.75, 3594, 0.50, 9856, 2023, 'Supercritical', False),
    ('Obra-C', 1320, '2x660 MW', 85.0, 2182, 6.25, 3443, 0.50, 9856, 2023, 'Supercritical', False),
    ('Anpara-B', 1000, '2x500 MW', 85.0, 2390, 6.55, 3516, 0.50, 7446, 1994, 'Subcritical', False),
    ('Harduaganj Extn. II', 500, '2x250 MW', 85.0, 2430, 9.00, 3715, 0.50, 3733, 2012, 'Subcritical', False),
    ('Parichha Extn. II', 500, '2x250 MW', 85.0, 2430, 9.00, 3666, 0.50, 3733, 2012, 'Subcritical', False),
    ('Anpara-A', 630, '3x210 MW', 85.0, 2430, 9.00, 3440, 0.50, 4704, 1987, 'Subcritical', True),
    ('Parichha Extn.', 420, '2x210 MW', 85.0, 2430, 9.00, 3713, 0.50, 3127, 2006, 'Subcritical', True),
    ('Harduaganj', 110, '1x110 MW', 60.0, 2625, 9.50, 3715, 2.50, 580, 1978, 'Subcritical', False),
    ('Obra-B', 1000, '5x200 MW', 75.0, 2755, 9.70, 3692, 2.10, 6588, 1980, 'Subcritical', True),
]

df = pd.DataFrame(data, columns=[
    'plant', 'capacity_mw', 'units_config', 'plf_pct', 'shr_kcal_kwh', 'apc_pct',
    'gcv_coal_kcal_kg', 'specific_oil_consumption_ml_kwh', 'energy_generated_mu',
    'com_year', 'technology', 'in_workbook'
])

df['scc_kg_kwh'] = df['shr_kcal_kwh'] / df['gcv_coal_kcal_kg']
df['age_years'] = 2024 - df['com_year']

df.to_csv('data/benchmark_9plants.csv', index=False)
print(df.round(3).to_string())
