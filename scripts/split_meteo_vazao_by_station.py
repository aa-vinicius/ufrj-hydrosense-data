import pandas as pd
import json
import os

# Carregar dados finais
with open('data/meteo_vazao_shifted.json') as f:
    df = pd.DataFrame(json.load(f))

# Carregar mapeamento estação-subbacia
with open('data/station_subbasin_mapping.json') as f:
    station_subbasin = json.load(f)

# IDs de estação presentes na planilha de vazão (obtidos via pandas ou manualmente)
ids_vazao = set([
    '58030000', '58060000', '19091', '58099000', '58105300', '58183000', '58204000', '58218000', '58235100', '19093', '58242000'
])

# Para cada estação, filtrar as subbacias associadas e salvar CSV apenas se estiver na lista de estações de vazão
output_dir = 'data/por_estacao'
os.makedirs(output_dir, exist_ok=True)

for station_id, subbacias in station_subbasin.items():
    if str(station_id) not in ids_vazao:
        continue
    subbacias_int = [int(s) for s in subbacias]
    # Filtrar por subbacia E station_id
    df_station = df[(df['subbasin_id'].isin(subbacias_int)) & (df['station_id'].astype(str) == str(station_id))]
    out_path = os.path.join(output_dir, f'meteo_vazao_shifted_station_{station_id}.csv')
    df_station.to_csv(out_path, index=False)
    print(f'Arquivo gerado: {out_path} ({len(df_station)} registros)')
