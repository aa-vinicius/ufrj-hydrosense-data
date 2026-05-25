import re
import pandas as pd
import json

file_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/raw_vazao/PtsLight_VazaoObs_1998_2025.xlsx"

def dms_to_dd(dms_str):
    if pd.isna(dms_str) or not isinstance(dms_str, str):
        return dms_str
    
    dms_str = dms_str.replace("'", "'").replace('"', '"').replace("”", '"').strip()
    match = re.match(r"(\d+)°\s*(\d+)'\s*([\d.]+)\"\s*([SSNNOOWW])", dms_str)
    if not match:
        match = re.match(r"(\d+)°\s*(\d+)\s*([\d.]+)\s*([SSNNOOWW])", dms_str)
        if not match:
            return dms_str
            
    degrees = float(match.group(1))
    minutes = float(match.group(2))
    seconds = float(match.group(3))
    direction = match.group(4).upper()
    
    dd = degrees + minutes / 60.0 + seconds / 3600.0
    
    if direction in ['S', 'O', 'W']:
        dd = -dd
        
    return dd

try:
    xl = pd.ExcelFile(file_path)
    
    df_sc = pd.read_excel(file_path, sheet_name='Coordenadas_SANTACECILIA')
    df_aux_sc = df_sc[['Subbasin', 'Lat', 'Lon']]
    
    aux_sc_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/silver_vazao/aux_coordenadas_santacecilia.csv"
    df_aux_sc.to_csv(aux_sc_path, index=False)
    print(f"Arquivo auxiliar salvo em: {aux_sc_path}")
    
    df_flu = pd.read_excel(file_path, sheet_name='Coordenadas_FLU')
    df_flu['Lat_Dec'] = df_flu['Lat'].apply(dms_to_dd)
    df_flu['Lon_Dec'] = df_flu['Lon'].apply(dms_to_dd)
    
    print("\nCoordenadas FLU convertidas com sucesso.")
    print(df_flu[['Código', 'Nome Light', 'Lat_Dec', 'Lon_Dec']])
    
    df_pirai = pd.read_excel(file_path, sheet_name='COORDENADAS_PIRAI')
    df_aux_pirai = df_pirai[['Subbasin', 'Lat', 'Lon']]
    aux_pirai_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/silver_vazao/aux_coordenadas_pirai.csv"
    df_aux_pirai.to_csv(aux_pirai_path, index=False)
    print(f"Arquivo auxiliar Piraí salvo em: {aux_pirai_path}")
    
    all_lats = pd.concat([df_sc['Lat'], df_pirai['Lat'], df_flu['Lat_Dec']]).dropna()
    all_lons = pd.concat([df_sc['Lon'], df_pirai['Lon'], df_flu['Lon_Dec']]).dropna()
    
    bbox = {
        "min_lat": float(all_lats.min()),
        "max_lat": float(all_lats.max()),
        "min_lon": float(all_lons.min()),
        "max_lon": float(all_lons.max())
    }
    
    bbox_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/silver_vazao/bounding_box_era5.json"
    with open(bbox_path, 'w', encoding='utf-8') as f:
        json.dump(bbox, f, indent=4, ensure_ascii=False)
        
    print(f"\nBounding Box unificada para ERA5 salva em: {bbox_path}")
    print(json.dumps(bbox, indent=4))

except Exception as e:
    print("Erro durante o processamento:", e)
