import pandas as pd
import json

# Carregar dados já unidos
with open('data/meteo_vazao_joined.json') as f:
    df = pd.DataFrame(json.load(f))

# Ordenar para garantir consistência
cols = ['subbasin_id', 'year', 'month']
df = df.sort_values(cols)

# Criar coluna de data para facilitar o deslocamento
# Considera o primeiro dia do mês
from datetime import datetime

def make_date(row):
    return datetime(int(row['year']), int(row['month']), 1)

df['date'] = df.apply(make_date, axis=1)

# Deslocar a vazão para o mês seguinte por subbacia
# Para cada subbacia, alinhar as variáveis meteorológicas do mês X com a vazão do mês X+1

def shift_flow(group):
    group = group.sort_values('date')
    group['flow_next_month'] = group['flow'].shift(-1)
    return group

df = df.groupby('subbasin_id').apply(shift_flow).reset_index(drop=True)

# Filtrar apenas registros com flow_next_month > 0 e não nulo
filtered = df[(df['flow_next_month'].notnull()) & (df['flow_next_month'] > 0)]

# Remover colunas auxiliares
filtered = filtered.drop(columns=['flow', 'date'])

# Salvar resultado
with open('data/meteo_vazao_shifted.json', 'w') as f:
    json.dump(filtered.to_dict('records'), f, indent=2)

print('Arquivo data/meteo_vazao_shifted.json gerado com deslocamento temporal e filtragem.')
