import os
import shutil
import pandas as pd
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.abspath(os.path.join(SCRIPT_DIR, "../data/raw_vazao/PtsLight_VazaoObs_1998_2025-v2.xlsx"))
silver_dir = os.path.abspath(os.path.join(SCRIPT_DIR, "../data/silver_vazao"))

try:
    # 1. Limpar a pasta silver_vazao
    print(f"Limpando o diretório: {silver_dir}")
    if os.path.exists(silver_dir):
        for filename in os.listdir(silver_dir):
            file_path = os.path.join(silver_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Falha ao deletar {file_path}. Motivo: {e}')
    else:
        os.makedirs(silver_dir, exist_ok=True)

    # 2. Carregar as planilhas
    print("\nCarregando planilhas do Excel...")
    df_sub = pd.read_excel(excel_path, sheet_name='Subbacias')
    df_pirai = pd.read_excel(excel_path, sheet_name='COORDENADAS_PIRAI')
    df_sc = pd.read_excel(excel_path, sheet_name='Coordenadas_SANTACECILIA')
    df_vazao = pd.read_excel(excel_path, sheet_name='Vazao_PtsLight')

    # 3. Recriar o arquivo aux_vazao_pts_light.csv
    vazao_csv_path = os.path.join(silver_dir, "aux_vazao_pts_light.csv")
    df_vazao.to_csv(vazao_csv_path, index=False)
    print(f"Arquivo de vazão original recriado em: {vazao_csv_path}")

    # 4. Criar mapeamento atualizado (excluindo a estação 19097)
    print("\nCriando mapeamento de subbacias atualizado...")
    df_map = df_sub[df_sub['Estações'] != 19097].copy()
    
    subbasin_col = [col for col in df_map.columns if 'Subbacias' in col][0]
    df_map = df_map[['Estações', subbasin_col]].rename(columns={subbasin_col: 'Subbacias'})
    
    df_map.loc[df_map['Estações'] == 19098, 'Subbacias'] = "2,3,4,5"
    df_map.loc[df_map['Estações'] == 58350001, 'Subbacias'] = "1,2,3,4,5,6,7,8"
    df_map.loc[df_map['Estações'] == 19094, 'Subbacias'] = "1-54"

    mapping_csv_path = os.path.join(silver_dir, "aux_mapeamento_subbacias.csv")
    df_map.to_csv(mapping_csv_path, index=False)
    print(f"Mapeamento atualizado salvando em: {mapping_csv_path}")
    print(df_map.to_string(index=False))

    # 5. Extrair coordenadas específicas para cada estação
    # Estação 19098: Subbacias 2,3,4,5 do Piraí
    df_coords_19098 = df_pirai[df_pirai['Subbasin'].isin([2, 3, 4, 5])][['Subbasin', 'Lat', 'Lon', 'Elev', 'Area']].copy()
    coords_19098_path = os.path.join(silver_dir, "coords_estacao_19098.csv")
    df_coords_19098.to_csv(coords_19098_path, index=False)
    print(f"\nCoordenadas da Estação 19098 salvas em: {coords_19098_path}")

    # Estação 58350001: Subbacias 1,2,3,4,5,6,7,8 do Piraí
    df_coords_58350001 = df_pirai[df_pirai['Subbasin'].isin([1, 2, 3, 4, 5, 6, 7, 8])][['Subbasin', 'Lat', 'Lon', 'Elev', 'Area']].copy()
    coords_58350001_path = os.path.join(silver_dir, "coords_estacao_58350001.csv")
    df_coords_58350001.to_csv(coords_58350001_path, index=False)
    print(f"Coordenadas da Estação 58350001 salvas em: {coords_58350001_path}")

    # Estação 19094: Subbacias 1-54 do Santa Cecília
    df_coords_19094 = df_sc[['Subbasin', 'Lat', 'Lon', 'Elev', 'Area']].copy()
    coords_19094_path = os.path.join(silver_dir, "coords_estacao_19094.csv")
    df_coords_19094.to_csv(coords_19094_path, index=False)
    print(f"Coordenadas da Estação 19094 salvas em: {coords_19094_path}")

    # 6. Calcular Bounding Box Individual para cada estação (para download do ERA5)
    bbox_dict = {}
    
    for station_id, df_coords in [("19098", df_coords_19098), ("58350001", df_coords_58350001), ("19094", df_coords_19094)]:
        bbox_dict[station_id] = {
            "min_lat": float(df_coords['Lat'].min()),
            "max_lat": float(df_coords['Lat'].max()),
            "min_lon": float(df_coords['Lon'].min()),
            "max_lon": float(df_coords['Lon'].max())
        }
    
    bbox_path = os.path.join(silver_dir, "bounding_boxes_era5.json")
    with open(bbox_path, 'w', encoding='utf-8') as f:
        json.dump(bbox_dict, f, indent=4, ensure_ascii=False)
        
    print(f"\nBounding Boxes individuais do ERA5 salvas em: {bbox_path}")
    print(json.dumps(bbox_dict, indent=4))

except Exception as e:
    print("Erro durante o processamento de reestruturação:", e)
