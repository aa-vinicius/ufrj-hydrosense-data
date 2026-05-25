import pandas as pd
import os
import argparse

# 1. Determinar o diretório do script para caminhos robustos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    parser = argparse.ArgumentParser(description="Process hourly ERA5 data into daily aggregates per station.")
    parser.add_argument("--station", type=str, required=True, help="Estação específica para processar (ex: 19098).")
    args = parser.parse_args()

    station_str = args.station.strip()
    file_path = os.path.abspath(os.path.join(SCRIPT_DIR, f'../../data/silver_era5/series_temporais_concatenadas_{station_str}.csv'))
    output_file = os.path.abspath(os.path.join(SCRIPT_DIR, f'../../data/silver_era5/dados_diarios_agregados_{station_str}.csv'))

    if not os.path.exists(file_path):
        print(f"Erro: Arquivo consolidado {file_path} não encontrado.")
        exit(1)

    print(f"Lendo {file_path}...")
    df = pd.read_csv(file_path)

    # Converter valid_time para datetime
    df['valid_time'] = pd.to_datetime(df['valid_time'])

    # Criar a coluna 'day' para o agrupamento
    df['day'] = df['valid_time'].dt.date

    # Agrupar e calcular Médias, Somas, Máximos e Mínimos
    agg_logic = {
        'u10': ['mean', 'max', 'min'],
        'v10': ['mean', 'max', 'min'],
        'd2m': ['mean', 'max', 'min'],
        't2m': ['mean', 'max', 'min'],
        'ssrd': ['mean', 'max', 'min'],
        'tp': ['sum', 'max', 'min']
    }

    print("Agrupando dados e calculando estatísticas diárias...")
    df_diario = df.groupby(['subbasin_id', 'latitude', 'longitude', 'centroid_lat', 'centroid_lon', 'day']).agg(agg_logic)

    # Ajustar os nomes das colunas para ficarem legíveis (ex: t2m_mean, tp_sum)
    df_diario.columns = [f"{col}_{func}" for col, func in df_diario.columns]

    # Resetar o index para voltar ao formato de tabela padrão
    df_diario = df_diario.reset_index()

    # Salvar o resultado
    df_diario.to_csv(output_file, index=False)

    print(f"Sucesso! Arquivo processado salvo como: {output_file}")
    print(f"Total de dias/registros gerados: {len(df_diario)}")

if __name__ == "__main__":
    main()
