import openpyxl
import json

wb = openpyxl.load_workbook('/mnt/user-data/uploads/Book2.xlsx', data_only=True)

plants_meta = {
    'ANPARA-A': {'name': 'Anpara-A', 'capacity_mw': 630, 'units': '3x210 MW', 'com_year': 1987, 'tech': 'Subcritical'},
    'PARICHHA EXT.': {'name': 'Parichha Extn.', 'capacity_mw': 420, 'units': '2x210 MW', 'com_year': 2006, 'tech': 'Subcritical'},
    'OBRA-B': {'name': 'Obra-B', 'capacity_mw': 1000, 'units': '5x200 MW', 'com_year': 1980, 'tech': 'Subcritical'},
}

years = ['FY 2019-20', 'FY 2020-21', 'FY 2021-22', 'FY 2022-23', 'FY 2023-24']

param_rows = {
    'capital_cost_cr': 4, 'equity_cr': 5, 'loan_cr': 6, 'depreciated_cost_cr': 7,
    'om_actual_cr': 9, 'target_availability_pct': 10, 'plf_pct': 12,
    'energy_generated_mu': 13, 'aux_consumption_pct': 14, 'shr_kcal_kwh': 15,
    'specific_oil_consumption_ml_kwh': 16, 'coal_consumption_mt': 19,
    'oil_consumption_kl': 23, 'avg_receivables_cr': 27, 'spares_pct': 28,
    'gcv_coal_kcal_kg': 29, 'gcv_oil_kcal_lt': 30, 'avg_coal_price_per_mt': 31,
    'avg_oil_price_per_kl': 32,
}


def get_rows(sheet_name):
    ws = wb[sheet_name]
    return list(ws.iter_rows(values_only=True))


header_index = {'ANPARA-A': 0, 'PARICHHA EXT.': 2, 'OBRA-B': 3}

data = {}
for sheet, meta in plants_meta.items():
    rows = get_rows(sheet)
    d = {'meta': meta, 'years': years, 'series': {}}
    col_start = 3 if sheet == 'OBRA-B' else 2
    hidx = header_index[sheet]
    for param, sno in param_rows.items():
        r = rows[hidx + sno]
        vals = list(r[col_start:col_start + 5])
        d['series'][param] = vals
    data[sheet] = d

with open('data/raw_extracted.json', 'w') as f:
    json.dump(data, f, indent=2, default=str)

print(json.dumps(data, indent=2, default=str))
