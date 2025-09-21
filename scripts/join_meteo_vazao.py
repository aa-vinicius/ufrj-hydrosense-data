import pandas as pd
import json

# Carregar dados meteorológicos
meteo = pd.read_csv('data/glob_1993a2023_mo.csv')

# Carregar mapeamento estação-sub-bacia
with open('data/station_subbasin_mapping.json') as f:
    station_subbasin = json.load(f)

# Carregar mapeamento estação meteo-sub-bacia
with open('data/meteo_station_subbasin_mapping.json') as f:
    meteo_subbasin = json.load(f)

# Carregar dados de vazão mensal
vazao = pd.read_json('data/vazao_mensal.json')

# Explodir o mapeamento estação-sub-bacia para (station_id, subbasin_id)
station_subbacia_pairs = []
for station, subbacias in station_subbasin.items():
    for sub in subbacias:
        station_subbacia_pairs.append({'station_id': station, 'subbasin_id': int(sub)})
station_subbacia_df = pd.DataFrame(station_subbacia_pairs)


# Garantir que station_id é string em ambos os DataFrames
vazao['station_id'] = vazao['station_id'].astype(str)
station_subbacia_df['station_id'] = station_subbacia_df['station_id'].astype(str)
vazao = vazao.merge(station_subbacia_df, on='station_id', how='left')

import pandas as pd
import json

# Carregar dados meteorológicos já com subbacia
with open('data/meteo_station_subbasin_mapping.json') as f:
    meteo = pd.DataFrame(json.load(f))

# Carregar mapeamento estação-sub-bacia
with open('data/station_subbasin_mapping.json') as f:
    station_subbasin = json.load(f)

# Carregar dados de vazão mensal
vazao = pd.read_json('data/vazao_mensal.json')

# Explodir o mapeamento estação-sub-bacia para (station_id, subbasin_id)
station_subbacia_pairs = []
for station, subbacias in station_subbasin.items():
    for sub in subbacias:
        station_subbacia_pairs.append({'station_id': station, 'subbasin_id': int(sub)})
station_subbacia_df = pd.DataFrame(station_subbacia_pairs)

# Unir dados de vazão com subbacia
vazao['station_id'] = vazao['station_id'].astype(str)
station_subbacia_df['station_id'] = station_subbacia_df['station_id'].astype(str)
vazao = vazao.merge(station_subbacia_df, on='station_id', how='left')
vazao['subbasin_id'] = vazao['subbasin_id'].astype(int)

# Garantir coluna subbasin_id no DataFrame meteorológico
if 'Subbasin' in meteo.columns:
    meteo['subbasin_id'] = meteo['Subbasin'].astype(int)
elif 'subbasin_id' not in meteo.columns:
    raise Exception('Coluna de subbacia não encontrada no DataFrame meteorológico.')

# Selecionar colunas relevantes
meteo_cols = ['year', 'month', 'subbasin_id', 'u2', 'tmin', 'tmax', 'rs', 'rh', 'eto', 'pr']
vazao_cols = ['year', 'month', 'subbasin_id', 'station_id', 'flow']

# Unir
df = pd.merge(meteo[meteo_cols], vazao[vazao_cols], on=['year', 'month', 'subbasin_id'], how='inner')

# Salvar como JSON
with open('data/meteo_vazao_joined.json', 'w') as f:
    json.dump(df.to_dict('records'), f, indent=2)

print('Junção meteorologia + vazão concluída. Arquivo salvo em data/meteo_vazao_joined.json')
