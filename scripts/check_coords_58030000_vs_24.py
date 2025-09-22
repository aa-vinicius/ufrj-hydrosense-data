import json
import pandas as pd

# Carregar join espacial
with open('data/meteo_station_subbasin_mapping.json') as f:
    meteo_subbasin = pd.DataFrame(json.load(f))

# Coordenadas únicas por subbacia 24
coords_24 = meteo_subbasin[meteo_subbasin['Subbasin'] == 24][['latitude', 'longitude']]
coords_24_unique = set(tuple(x) for x in coords_24.values)
print(f'Coordenadas únicas subbacia 24: {sorted(coords_24_unique)}')
print(f'Total únicas subbacia 24: {len(coords_24_unique)}')

# Coordenadas únicas consideradas no stats_split_by_station.py para 58030000
with open('data/station_subbasin_mapping.json') as f:
    station_subbasin = json.load(f)
subbacias_58030000 = [int(s) for s in station_subbasin['58030000']]
coords_stats = set()
for sub in subbacias_58030000:
    sub_coords = meteo_subbasin[meteo_subbasin['Subbasin'] == sub][['latitude', 'longitude']]
    for coord in set(tuple(x) for x in sub_coords.values):
        coords_stats.add(coord)
print(f'Coordenadas únicas stats_split_by_station.py para 58030000: {sorted(coords_stats)}')
print(f'Total stats_split_by_station.py para 58030000: {len(coords_stats)}')

# Diferença
print(f'Coordenadas em stats_split_by_station.py e não em subbacia 24: {sorted(coords_stats - coords_24_unique)}')
print(f'Coordenadas em subbacia 24 e não em stats_split_by_station.py: {sorted(coords_24_unique - coords_stats)}')
