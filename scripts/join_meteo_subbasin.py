import pandas as pd
import geopandas as gpd
import json
from shapely.geometry import Point

# Carregar dados meteorológicos
meteo = pd.read_csv('data/glob_1993a2023_mo.csv')

# Carregar shapefile das subbacias
subbacias = gpd.read_file('data/Subbasin_FUNIL/Subbacias_FUNIL-4326WGS84.shp')

# Criar GeoDataFrame das estações meteorológicas
geometry = [Point(xy) for xy in zip(meteo['longitude'], meteo['latitude'])]
gdf_meteo = gpd.GeoDataFrame(meteo, geometry=geometry, crs=subbacias.crs)

# Join espacial: cada estação recebe o ID da subbacia
joined = gpd.sjoin(gdf_meteo, subbacias[['Subbasin', 'geometry']], how='left', predicate='within')


# Remover linhas sem subbacia associada
result = joined.dropna(subset=['Subbasin'])
result['Subbasin'] = result['Subbasin'].astype(int)

# Remover coluna 'Unnamed: 0' se existir
cols_to_drop = ['geometry', 'index_right']
if 'Unnamed: 0' in result.columns:
    cols_to_drop.append('Unnamed: 0')
records = result.drop(columns=cols_to_drop).to_dict('records')
with open('data/meteo_station_subbasin_mapping.json', 'w') as f:
    json.dump(records, f, indent=2)

print('Join espacial concluído. Arquivo salvo em data/meteo_station_subbasin_mapping.json')
