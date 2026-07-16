import json
import pandas as pd

raw = json.load(open('data/raw_extracted.json'))

rows = []
for sheet, d in raw.items():
    meta = d['meta']
    years = d['years']
    s = d['series']
    for i, yr in enumerate(years):
        def g(key):
            v = s[key][i]
            return v if v is not None else float('nan')

        row = {
            'plant': meta['name'],
            'units_config': meta['units'],
            'capacity_mw': meta['capacity_mw'],
            'com_year': meta['com_year'],
            'technology': meta['tech'],
            'year': yr,
            'year_index': i,
            'capital_cost_cr': g('capital_cost_cr'),
            'equity_cr': g('equity_cr'),
            'loan_cr': g('loan_cr'),
            'depreciated_cost_cr': g('depreciated_cost_cr'),
            'om_actual_cr': g('om_actual_cr'),
            'target_availability_pct': g('target_availability_pct') * 100 if s['target_availability_pct'][i] is not None else float('nan'),
            'plf_pct': g('plf_pct') * 100 if s['plf_pct'][i] is not None else float('nan'),
            'energy_generated_mu': g('energy_generated_mu'),
            'apc_pct': g('aux_consumption_pct') * 100 if s['aux_consumption_pct'][i] is not None else float('nan'),
            'shr_kcal_kwh': g('shr_kcal_kwh'),
            'specific_oil_consumption_ml_kwh': g('specific_oil_consumption_ml_kwh'),
            'coal_consumption_mt': g('coal_consumption_mt'),
            'oil_consumption_kl': g('oil_consumption_kl'),
            'avg_receivables_cr': g('avg_receivables_cr'),
            'spares_pct': g('spares_pct') * 100 if s['spares_pct'][i] is not None else float('nan'),
            'gcv_coal_kcal_kg': g('gcv_coal_kcal_kg'),
            'gcv_oil_kcal_lt': g('gcv_oil_kcal_lt'),
            'avg_coal_price_per_mt': g('avg_coal_price_per_mt'),
            'avg_oil_price_per_kl': g('avg_oil_price_per_kl'),
        }
        rows.append(row)

df = pd.DataFrame(rows)

# ---- Derived technical metrics ----
df['scc_kg_kwh'] = df['shr_kcal_kwh'] / df['gcv_coal_kcal_kg']
df['debt_equity_ratio'] = df['loan_cr'] / df['equity_cr'].replace(0, pd.NA)
df['capital_cost_per_mw_cr'] = df['capital_cost_cr'] / df['capacity_mw']

# ---- Derived cost metrics (Rs per kWh / paise per unit) ----
# O&M cost per unit: O&M (Rs Cr) *1e7 / (Energy MU * 1e6 kWh) = Rs/kWh
df['om_cost_paise_per_unit'] = (df['om_actual_cr'] * 1e7) / (df['energy_generated_mu'] * 1e6) * 100

# Coal cost per unit: SCC (kg/kWh) * price (Rs/MT) / 1000 (Rs/kg) = Rs/kWh
df['coal_cost_paise_per_unit'] = df['scc_kg_kwh'] * (df['avg_coal_price_per_mt'] / 1000) * 100

# Oil cost per unit: spec oil consumption (ml/kWh) -> KL = ml/1e6 ; * price per KL = Rs/kWh
df['oil_cost_paise_per_unit'] = (df['specific_oil_consumption_ml_kwh'] / 1e6) * df['avg_oil_price_per_kl'] * 100

df['fuel_cost_paise_per_unit'] = df['coal_cost_paise_per_unit'] + df['oil_cost_paise_per_unit']
df['total_variable_cost_paise_per_unit'] = df['fuel_cost_paise_per_unit'] + df['om_cost_paise_per_unit']

# Receivables in months of O&M-ish scale (rough liquidity indicator): receivables / (energy*avg realization not available)
# Depreciation trend (WDV run-down) - % of capital cost remaining
df['net_block_pct_of_capital'] = (df['depreciated_cost_cr'] / df['capital_cost_cr']) * 100

df.to_csv('data/timeseries.csv', index=False)
print(df.round(3).to_string())
print()
print(df.columns.tolist())
