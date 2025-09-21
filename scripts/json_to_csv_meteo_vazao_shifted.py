import pandas as pd
import json

# Carregar o arquivo JSON final
with open('data/meteo_vazao_shifted.json') as f:
    data = json.load(f)
    df = pd.DataFrame(data)

# Salvar como CSV
csv_path = 'data/meteo_vazao_shifted.csv'
df.to_csv(csv_path, index=False)
print(f'Arquivo salvo em {csv_path}')
