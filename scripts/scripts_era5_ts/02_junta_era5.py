import os
import zipfile
import pandas as pd
import io
import re
import argparse
import glob

# 1. Determinar o diretório do script para caminhos robustos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/raw_era5'))
SILVER_VAZAO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/silver_vazao'))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/silver_era5'))

data_inicio = '1998-01-01'
data_fim = '2025-12-30'

# Garantir que o diretório de destino existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Merge ERA5 hourly timeseries per station.")
    parser.add_argument("--station", type=str, required=True, help="Estação específica para processar (ex: 19098).")
    args = parser.parse_args()

    station_str = args.station.strip()
    coords_file = os.path.join(SILVER_VAZAO_DIR, f"coords_estacao_{station_str}.csv")
    arquivo_saida = os.path.join(OUTPUT_DIR, f"series_temporais_concatenadas_{station_str}.csv")

    if not os.path.exists(coords_file):
        print(f"Erro: Arquivo de coordenadas {coords_file} não encontrado.")
        return

    # Carregar coordenadas da estação
    df_coords = pd.read_csv(coords_file)
    subbasins = df_coords['Subbasin'].unique()

    dfs_subbacias = []
    print(f"Iniciando processamento para Estação {station_str} (Filtro: {data_inicio} a {data_fim})...")

    # Mapear os arquivos zip locais às sub-bacias
    for subid in subbasins:
        row_coord = df_coords[df_coords['Subbasin'] == subid].iloc[0]
        c_lat, c_lon = str(row_coord['Lat']), str(row_coord['Lon'])
        
        # Procurar arquivo que corresponda ao ID e coordenadas específicas
        possible_names = []
        try:
            int_subid = int(float(subid))
            possible_names.append(os.path.join(INPUT_DIR, f"dados_{int_subid}_{c_lat}_{c_lon}.csv.zip"))
            possible_names.append(os.path.join(INPUT_DIR, f"dados_{float(subid)}_{c_lat}_{c_lon}.csv.zip"))
        except Exception:
            possible_names.append(os.path.join(INPUT_DIR, f"dados_{subid}_{c_lat}_{c_lon}.csv.zip"))
            
        files = [f for f in possible_names if os.path.exists(f)]
        if not files:
            # Fallback usando glob com o prefixo correto para lidar com pequenas diferenças de string
            try:
                int_subid = int(float(subid))
                pattern = os.path.join(INPUT_DIR, f"dados_{int_subid}_{c_lat}*_{c_lon}*.csv.zip")
                files = glob.glob(pattern)
            except Exception:
                files = []
                
        if not files:
            print(f"Aviso: Arquivo de dados para sub-bacia {subid} (Lat: {c_lat}, Lon: {c_lon}) não encontrado na pasta {INPUT_DIR}.")
            continue

        caminho_zip = files[0]
        nome_filho = os.path.basename(caminho_zip)
        print(f"Processando Sub-bacia {subid} ({nome_filho})...")

        # Abrir o arquivo zip da sub-bacia
        with zipfile.ZipFile(caminho_zip, 'r') as zip_interno:
            arquivos_csv = [f for f in zip_interno.namelist() if f.endswith('.csv')]
            df_sub_merge = None
            
            for csv_nome in arquivos_csv:
                with zip_interno.open(csv_nome) as f_csv:
                    df_temp = pd.read_csv(f_csv)
                    
                    # Converter e Filtrar por data imediatamente para poupar memória
                    df_temp['valid_time'] = pd.to_datetime(df_temp['valid_time'])
                    mask = (df_temp['valid_time'] >= data_inicio) & (df_temp['valid_time'] <= data_fim)
                    df_temp = df_temp.loc[mask]
                    
                    if df_temp.empty:
                        continue

                    if df_sub_merge is None:
                        df_sub_merge = df_temp
                    else:
                        df_sub_merge = pd.merge(
                            df_sub_merge, 
                            df_temp, 
                            on=['valid_time', 'latitude', 'longitude'], 
                            how='outer'
                        )
            
            if df_sub_merge is not None and not df_sub_merge.empty:
                df_sub_merge['subbasin_id'] = int(float(subid))
                df_sub_merge['centroid_lat'] = float(c_lat)
                df_sub_merge['centroid_lon'] = float(c_lon)
                dfs_subbacias.append(df_sub_merge)

    if dfs_subbacias:
        print("Concatenando e formatando arquivo final...")
        df_final = pd.concat(dfs_subbacias, ignore_index=True)
        
        # Ordem de colunas desejada
        colunas_ordem = [
            'valid_time', 'd2m', 't2m', 'tp', 'ssrd', 'u10', 'v10', 
            'latitude', 'longitude', 'subbasin_id', 'centroid_lat', 'centroid_lon'
        ]
        
        colunas_existentes = [c for c in colunas_ordem if c in df_final.columns]
        df_final = df_final[colunas_existentes]
        
        # Ordenação final
        df_final = df_final.sort_values(['subbasin_id', 'valid_time'])
        
        df_final.to_csv(arquivo_saida, index=False)
        print(f"Sucesso! Salvo em: {arquivo_saida}")
        print(f"Período processado: {df_final['valid_time'].min()} a {df_final['valid_time'].max()}")
    else:
        print("Nenhum dado encontrado para o período especificado.")

if __name__ == "__main__":
    main()
