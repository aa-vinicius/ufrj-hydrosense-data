import os
import pandas as pd
import cdsapi
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. Determinar o diretório do script para caminhos robustos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SILVER_VAZAO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/silver_vazao"))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../data/raw_era5"))
DATASET = "reanalysis-era5-land-timeseries"
MAX_WORKERS = 5  # O Copernicus gerencia a fila, threads extras enviam requests em paralelo

DATE_RANGE = "1998-01-01/2025-12-30"

VARIABLES = [
    "2m_dewpoint_temperature",
    "surface_solar_radiation_downwards",
    "surface_thermal_radiation_downwards",
    "2m_temperature",
    "total_precipitation",
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
]

# Garantir que o diretório de destino existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

def download_subbasin(subid, lat, lon):
    import glob
    
    # Verificar se já existe um arquivo válido para este ID de subbacia (tanto no formato int quanto float no nome)
    try:
        int_subid = int(float(subid))
        pattern_int = os.path.join(OUTPUT_DIR, f"dados_{int_subid}_*.csv.zip")
        pattern_float = os.path.join(OUTPUT_DIR, f"dados_{float(subid)}_*.csv.zip")
        existing_files = glob.glob(pattern_int) + glob.glob(pattern_float)
    except Exception:
        pattern = os.path.join(OUTPUT_DIR, f"dados_{subid}_*.csv.zip")
        existing_files = glob.glob(pattern)
        
    existing_files = list(set(existing_files))
    
    if existing_files:
        # Garantir que o arquivo existente não está vazio/corrompido
        if any(os.path.exists(f) and os.path.getsize(f) > 0 for f in existing_files):
            print(f"Sub-bacia {subid} já foi baixada ({os.path.basename(existing_files[0])}). Pulando...")
            return subid, True

    nome_arquivo = os.path.join(OUTPUT_DIR, f"dados_{subid}_{lat}_{lon}.csv.zip")
    print(f"Iniciando solicitação para Sub-bacia {subid} (Lat: {lat}, Lon: {lon})...")
    
    request = {
        "variable": VARIABLES,
        "location": {"longitude": lon, "latitude": lat},
        "date": [DATE_RANGE],
        "data_format": "csv"
    }

    try:
        # Cada thread deve ter seu próprio cliente cdsapi
        client = cdsapi.Client()
        client.retrieve(DATASET, request, nome_arquivo)
        print(f"Sucesso: Sub-bacia {subid} salva em {nome_arquivo}")
        return subid, True
    except Exception as e:
        print(f"Erro na Sub-bacia {subid}: {e}")
        return subid, False

def main():
    parser = argparse.ArgumentParser(description="Download ERA5-Land timeseries data per station.")
    parser.add_argument("--station", type=str, required=True, help="Estação específica para processar (ex: 19098).")
    args = parser.parse_args()

    station_str = args.station.strip()
    coords_file = os.path.join(SILVER_VAZAO_DIR, f"coords_estacao_{station_str}.csv")

    if not os.path.exists(coords_file):
        print(f"Erro: Arquivo de coordenadas {coords_file} não encontrado.")
        return

    # Carregar coordenadas da estação específica
    df_coords = pd.read_csv(coords_file)
    
    if df_coords.empty:
        print(f"Nenhuma coordenada encontrada para a estação {station_str}.")
        return

    print(f"Enviando solicitações de download para {len(df_coords)} sub-bacias da estação {station_str} em paralelo...")
    
    # Executar downloads em paralelo utilizando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_subbasin, str(row['Subbasin']), row['Lat'], row['Lon']): row
            for _, row in df_coords.iterrows()
        }
        
        for future in as_completed(futures):
            subid, success = future.result()
            status = "concluído com sucesso" if success else "com erro"
            print(f"Task da Sub-bacia {subid} finalizada ({status}).")

if __name__ == "__main__":
    main()
