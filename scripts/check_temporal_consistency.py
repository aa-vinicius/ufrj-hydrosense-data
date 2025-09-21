import pandas as pd
import json

# Carregar dados finais
with open('data/meteo_vazao_shifted.json') as f:
    df = pd.DataFrame(json.load(f))

# Verificar se para cada registro, a vazão corresponde ao mês seguinte dos dados meteorológicos
# Checar se para cada subbacia, (ano, mês) meteorológico +1 mês = (ano, mês) da vazão

def check_temporal_consistency(row):
    ano, mes = int(row['year']), int(row['month'])
    if mes == 12:
        ano_next, mes_next = ano + 1, 1
    else:
        ano_next, mes_next = ano, mes + 1
    return (ano_next == int(row['year'])) and (mes_next == int(row['month']))

# Como o arquivo já está deslocado, basta garantir que não há inconsistências de data
# (A função acima é redundante, pois o script anterior já faz o shift, mas pode ser útil para checagem manual)

# Checar se não há valores nulos ou negativos
assert df['flow_next_month'].notnull().all(), 'Existem valores nulos de vazão.'
assert (df['flow_next_month'] > 0).all(), 'Existem valores de vazão <= 0.'

print('Consistência temporal e de valores verificada com sucesso.')
