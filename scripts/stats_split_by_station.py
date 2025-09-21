import pandas as pd
import json
import os
from collections import defaultdict

# 1. Quantidade original de coordenadas no arquivo de dados meteorológicos
meteo = pd.read_csv('data/glob_1993a2023_mo.csv')
qtd_coords_meteo = meteo[['latitude', 'longitude']].drop_duplicates().shape[0]
print(f'Quantidade original de coordenadas meteorológicas: {qtd_coords_meteo}')

# 2. Quantidade de coordenadas por subbacia após o join espacial
with open('data/meteo_station_subbasin_mapping.json') as f:
    meteo_subbasin = pd.DataFrame(json.load(f))
qtd_coords_por_subbacia = meteo_subbasin.groupby('Subbasin')[['latitude', 'longitude']].nunique().reset_index()
print('\nQuantidade de coordenadas por subbacia após join espacial:')
print(qtd_coords_por_subbacia)

# 3. Quantidade de coordenadas esperada para cada estação fluviométrica a partir do mapeamento
with open('data/station_subbasin_mapping.json') as f:
    station_subbasin = json.load(f)

coords_por_estacao = {}
for station_id, subbacias in station_subbasin.items():
    subbacias_int = [int(s) for s in subbacias]
    coords = meteo_subbasin[meteo_subbasin['Subbasin'].isin(subbacias_int)][['latitude', 'longitude']].drop_duplicates()
    coords_por_estacao[station_id] = coords.shape[0]
print('\nQuantidade de coordenadas esperada para cada estação:')
for k, v in coords_por_estacao.items():
    print(f'Estação {k}: {v}')


# 4. Carregar DataFrame de meses válidos (vazão não nula e > 0)
df = pd.read_csv('data/meteo_vazao_shifted.csv')
df = df[df['flow_next_month'].notnull() & (df['flow_next_month'] > 0)]

# 4. Quantidade de registros esperada para cada estação (apenas meses válidos)
registros_esperados = {}
for station_id, subbacias in station_subbasin.items():
    subbacias_int = [int(s) for s in subbacias]
    # Filtrar registros válidos para a estação
    df_station = df[(df['station_id'].astype(str) == str(station_id)) & (df['subbasin_id'].isin(subbacias_int))]
    registros_esperados[station_id] = df_station.shape[0]
print('\nQuantidade de registros esperada para cada estação (apenas meses válidos):')
for k, v in registros_esperados.items():
    print(f'Estação {k}: {v}')

# 5. Comparação com arquivos gerados por_estacao
print('\nComparação com arquivos gerados:')
dir_path = 'data/por_estacao'
erros = []
for station_id in station_subbasin.keys():
    file_path = os.path.join(dir_path, f'meteo_vazao_shifted_station_{station_id}.csv')
    if not os.path.exists(file_path):
        print(f'Arquivo não encontrado: {file_path}')
        continue
    df_file = pd.read_csv(file_path)
    qtd_gerado = df_file.shape[0]
    qtd_esperado = registros_esperados[station_id]
    print(f'Estação {station_id}: gerado={qtd_gerado}, esperado={qtd_esperado}')
    if qtd_gerado != qtd_esperado:
        erros.append(f'Estação {station_id}: gerado={qtd_gerado}, esperado={qtd_esperado}')

if not erros:
    print('\nTodos os arquivos têm a quantidade esperada de registros!')
else:
    print('\nInconsistências encontradas:')
    for erro in erros:
        print(erro)
