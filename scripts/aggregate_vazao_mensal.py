import pandas as pd
import json

# Carregar dados de vazão
xls = pd.ExcelFile('data/FUNIL_VazaoObs_1998_2024.xlsx')
df = pd.read_excel(xls, sheet_name='Vazao_FUNIL', header=0)

# Ajustar nomes das colunas (ID das estações)
df.columns = [str(col) for col in df.columns]

# Converter coluna de datas
if not pd.api.types.is_datetime64_any_dtype(df.iloc[:,0]):
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0])

df = df.rename(columns={df.columns[0]: 'date'})

# Transformar para formato longo
long_df = df.melt(id_vars=['date'], var_name='station_id', value_name='flow')

# Adicionar ano e mês
long_df['year'] = long_df['date'].dt.year
long_df['month'] = long_df['date'].dt.month

# Agregar por estação, ano e mês (média, máximo e mínimo mensal)
monthly_agg = long_df.groupby(['station_id', 'year', 'month'], as_index=False)['flow'].agg({
    'flow': 'mean',
    'flow_max': 'max',
    'flow_min': 'min'
})

# Renomear colunas para clareza
monthly_agg = monthly_agg.rename(columns={'flow': 'flow'})

# Manter compatibilidade: criar arquivo original apenas com média
monthly = long_df.groupby(['station_id', 'year', 'month'], as_index=False)['flow'].mean()

# Salvar ambos os arquivos
monthly.to_json('data/vazao_mensal.json', orient='records', date_format='iso', indent=2)
monthly_agg.to_json('data/vazao_mensal_extended.json', orient='records', date_format='iso', indent=2)

print('Agregação mensal concluída.')
print('Arquivo original (apenas média) salvo em data/vazao_mensal.json')
print('Arquivo estendido (média, máx, mín) salvo em data/vazao_mensal_extended.json')
