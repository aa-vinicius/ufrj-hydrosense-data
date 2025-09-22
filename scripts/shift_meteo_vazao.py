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


# Deslocar a vazão para o mês seguinte por subbacia E estação
# Para cada (subbacia, estação), alinhar as variáveis meteorológicas do mês X com a vazão do mês X+1

def is_next_month(row, next_row):
    # Verifica se next_row é o mês seguinte de row
    if pd.isnull(next_row['year']) or pd.isnull(next_row['month']):
        return False
    year, month = int(row['year']), int(row['month'])
    next_year, next_month = int(next_row['year']), int(next_row['month'])
    if month == 12:
        return (next_year == year + 1) and (next_month == 1)
    else:
        return (next_year == year) and (next_month == month + 1)

def shift_flow_preciso(group):
    group = group.sort_values('date').reset_index(drop=True)
    flow_next = []
    for i in range(len(group)):
        if i < len(group) - 1 and is_next_month(group.iloc[i], group.iloc[i+1]):
            flow_next.append(group.iloc[i+1]['flow'])
        else:
            flow_next.append(None)
    group['flow_next_month'] = flow_next
    return group

df = df.groupby(['subbasin_id', 'station_id'], group_keys=False).apply(shift_flow_preciso).reset_index(drop=True)

# Filtrar apenas registros com flow_next_month > 0 e não nulo
filtered = df[(df['flow_next_month'].notnull()) & (df['flow_next_month'] > 0)]

# Remover colunas auxiliares
filtered = filtered.drop(columns=['flow', 'date'])

# Salvar resultado
with open('data/meteo_vazao_shifted.json', 'w') as f:
    json.dump(filtered.to_dict('records'), f, indent=2)

print('Arquivo data/meteo_vazao_shifted.json gerado com deslocamento temporal e filtragem.')
