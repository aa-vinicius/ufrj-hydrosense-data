import json
import pandas as pd
from collections import defaultdict

# Carregar join espacial
with open('data/meteo_station_subbasin_mapping.json') as f:
    meteo_subbasin = pd.DataFrame(json.load(f))

# 1. Listar todas as coordenadas associadas à subbacia 24
coords_24 = meteo_subbasin[meteo_subbasin['Subbasin'] == 24][['latitude', 'longitude']]
coords_24_tuples = [tuple(x) for x in coords_24.values]
print(f'Coordenadas associadas à subbacia 24:')
for lat, lon in coords_24_tuples:
    print(f'  lat={lat}, lon={lon}')
print(f'Total: {len(coords_24_tuples)}')

# 2. Verificar se alguma dessas coordenadas aparece em mais de uma subbacia
coord_to_subs = defaultdict(set)
for _, row in meteo_subbasin.iterrows():
    coord = (row['latitude'], row['longitude'])
    coord_to_subs[coord].add(row['Subbasin'])

print('\nCoordenadas de subbacia 24 que aparecem em outras subbacias:')
count_multi = 0
for coord in coords_24_tuples:
    if len(coord_to_subs[coord]) > 1:
        print(f'{coord} -> subbacias: {sorted(coord_to_subs[coord])}')
        count_multi += 1
if count_multi == 0:
    print('Nenhuma coordenada de subbacia 24 aparece em mais de uma subbacia.')
else:
    print(f'Total de coordenadas de subbacia 24 em múltiplas subbacias: {count_multi}')
