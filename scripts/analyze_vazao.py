import pandas as pd

file_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/raw_vazao/PtsLight_VazaoObs_1998_2025.xlsx"

try:
    print("--- Lendo a aba Vazao_PtsLight ---")
    df = pd.read_excel(file_path, sheet_name='Vazao_PtsLight')
    
    # 1. Salvar arquivo auxiliar com as 5 colunas
    aux_vazao_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/silver_vazao/aux_vazao_pts_light.csv"
    df.to_csv(aux_vazao_path, index=False)
    print(f"Arquivo auxiliar salvo com sucesso em: {aux_vazao_path}")
    print(f"Shape: {df.shape}")
    print("Colunas:", df.columns.tolist())
    
    # 2. Converter coluna de Data para datetime
    df['Data'] = pd.to_datetime(df['Data'])
    
    # 3. Verificar gaps de datas (dias faltantes na série temporal)
    min_date = df['Data'].min()
    max_date = df['Data'].max()
    print(f"\nSérie temporal de {min_date.strftime('%Y-%m-%d')} até {max_date.strftime('%Y-%m-%d')}")
    
    # Criar um range completo de datas sem falhas
    full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    missing_dates = full_date_range.difference(df['Data'])
    
    print("\n--- Verificação de datas faltantes (dias ausentes na tabela) ---")
    if len(missing_dates) == 0:
        print("Nenhuma data está ausente da série temporal. A sequência de dias está contínua.")
    else:
        print(f"Foram encontradas {len(missing_dates)} datas ausentes!")
        print("Algumas datas ausentes:", missing_dates[:10].strftime('%Y-%m-%d').tolist())
        
    # 4. Verificar valores nulos ou faltantes (NaN) nas colunas de vazão
    print("\n--- Verificação de valores nulos (NaN) nas colunas de vazão ---")
    vazao_cols = [19098, 58350001, 19094, 19097]
    for col in vazao_cols:
        null_count = df[col].isna().sum()
        print(f"Estação {col}: {null_count} valores nulos (NaN) de {len(df)} total.")
        if null_count > 0:
            null_rows = df[df[col].isna()]
            print(f"  Primeiras datas com valores nulos para {col}:", null_rows['Data'].head(5).dt.strftime('%Y-%m-%d').tolist())

except Exception as e:
    print("Erro na análise da planilha de vazão:", e)
