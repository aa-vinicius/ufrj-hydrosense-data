import os
import re

# IDs de estação presentes na planilha de vazão (obtidos via pandas)
ids_vazao = set([
    '58030000', '58060000', '19091', '58099000', '58105300', '58183000', '58204000', '58218000', '58235100', '19093', '58242000'
])

# Listar arquivos na pasta data/por_estacao
folder = 'data/por_estacao'
files = os.listdir(folder)
ids_arquivos = set()
for f in files:
    m = re.match(r'meteo_vazao_shifted_station_(\d+)\.csv', f)
    if m:
        ids_arquivos.add(m.group(1))

# Identificar arquivos que não estão na lista de estações da planilha de vazão
extra = sorted(list(ids_arquivos - ids_vazao))
missing = sorted(list(ids_vazao - ids_arquivos))

print('IDs de estação presentes em arquivos mas NÃO na planilha de vazão:')
for e in extra:
    print(e)
print('\nIDs de estação presentes na planilha de vazão mas NÃO em arquivos:')
for m in missing:
    print(m)
