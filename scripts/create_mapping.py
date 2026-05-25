import pandas as pd

file_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/raw_vazao/PtsLight_VazaoObs_1998_2025.xlsx"

try:
    print("--- Carregando aba Subbacias ---")
    df = pd.read_excel(file_path, sheet_name='Subbacias')
    
    # Selecionar coluna A (Estações) e coluna C (Subbacias )
    subbasin_col = [col for col in df.columns if 'Subbacias' in col][0]
    df_aux = df[['Estações', subbasin_col]].rename(columns={subbasin_col: 'Subbacias'})
    
    # Ajuste de negócio 1: a estação 19097 deve considerar as mesmas bacias da 19094 (1-54)
    val_19094 = df_aux.loc[df_aux['Estações'] == 19094, 'Subbacias'].values[0]
    df_aux.loc[df_aux['Estações'] == 19097, 'Subbacias'] = val_19094
    
    # Ajuste de negócio 2: a estação 58350001 é incremental à 19098,
    # então deve herdar as subbacias de 19098
    sub_19098_str = str(df_aux.loc[df_aux['Estações'] == 19098, 'Subbacias'].values[0])
    sub_58350001_str = str(df_aux.loc[df_aux['Estações'] == 58350001, 'Subbacias'].values[0])
    
    # Converter para sets de inteiros e fazer a união
    set_19098 = set(int(x.strip()) for x in sub_19098_str.split(',') if x.strip())
    set_58350001 = set(int(x.strip()) for x in sub_58350001_str.split(',') if x.strip())
    
    combined_set = set_19098.union(set_58350001)
    combined_str = ','.join(str(x) for x in sorted(combined_set))
    
    df_aux.loc[df_aux['Estações'] == 58350001, 'Subbacias'] = combined_str
    
    mapping_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/silver_vazao/aux_mapeamento_subbacias.csv"
    df_aux.to_csv(mapping_path, index=False)
    
    print(f"Mapeamento ajustado com incrementais salvo em: {mapping_path}")
    print(df_aux.to_string(index=False))

except Exception as e:
    print("Erro ao gerar/ajustar mapeamento:", e)
