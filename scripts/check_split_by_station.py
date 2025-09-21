import os
import pandas as pd
import json

# Carregar mapeamento estação-subbacia
with open('data/station_subbasin_mapping.json') as f:
    station_subbasin = json.load(f)

# Pasta dos arquivos por estação
dir_path = 'data/por_estacao'

# Verificação de consistência
erros = []
for station_id, subbacias in station_subbasin.items():
    subbacias_int = [int(s) for s in subbacias]
    file_path = os.path.join(dir_path, f'meteo_vazao_shifted_station_{station_id}.csv')
    if not os.path.exists(file_path):
        print(f'Arquivo não encontrado: {file_path}')
        continue
    df = pd.read_csv(file_path)
    # Verifica se todos os registros têm o station_id correto
    if not df.empty:
        if not (df['station_id'].astype(str) == str(station_id)).all():
            erros.append(f'Arquivo {file_path}: station_id inconsistente')
        # Verifica se todos os registros têm subbasin_id permitido
        if not df['subbasin_id'].isin(subbacias_int).all():
            erros.append(f'Arquivo {file_path}: subbasin_id inconsistente')

if not erros:
    print('Todos os arquivos estão consistentes!')
else:
    print('Inconsistências encontradas:')
    for erro in erros:
        print(erro)
