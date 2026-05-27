import pandas as pd
import os
import argparse

# 1. Determinar o diretório do script para caminhos robustos
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SILVER_VAZAO_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/silver_vazao'))
vazao_file = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/silver_vazao/aux_vazao_pts_light.csv'))
output_dir = os.path.abspath(os.path.join(SCRIPT_DIR, '../../data/gold'))

# Garantir que o diretório Gold de destino existe
os.makedirs(output_dir, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Merge ERA5 daily aggregated data with discharge series per station.")
    parser.add_argument("--station", type=str, required=True, help="Estação específica para processar (ex: 19098).")
    args = parser.parse_args()

    station_str = args.station.strip()
    era5_file = os.path.abspath(os.path.join(SCRIPT_DIR, f'../../data/silver_era5/dados_diarios_agregados_{station_str}.csv'))
    coords_file = os.path.join(SILVER_VAZAO_DIR, f"coords_estacao_{station_str}.csv")
    output_name = os.path.join(output_dir, f'dataset_modelagem_vazao_{station_str}.csv')

    print("Carregando arquivos...")
    if not os.path.exists(era5_file):
        print(f"Erro: Arquivo do ERA5 {era5_file} não encontrado. Execute as etapas anteriores do pipeline primeiro.")
        exit(1)
    if not os.path.exists(vazao_file):
        print(f"Erro: Arquivo de vazão {vazao_file} não encontrado.")
        exit(1)
    if not os.path.exists(coords_file):
        print(f"Erro: Arquivo de coordenadas da estação {coords_file} não encontrado.")
        exit(1)

    df_era5 = pd.read_csv(era5_file)
    df_vazao = pd.read_csv(vazao_file)
    df_coords = pd.read_csv(coords_file)

    # Padronizar colunas de data e tipos
    df_era5['day'] = pd.to_datetime(df_era5['day'])
    df_vazao['Data'] = pd.to_datetime(df_vazao['Data'])
    df_vazao = df_vazao.sort_values('Data').reset_index(drop=True)

    # 1. Garantia de Qualidade de Dados (Strict check):
    # Verificar se todas as subbacias listadas no coords_file estão presentes no dados_diarios_agregados
    subbasin_list = df_coords['Subbasin'].unique()
    subbasins_present = df_era5['subbasin_id'].unique()
    missing_subbasins = [s for s in subbasin_list if s not in subbasins_present]

    if missing_subbasins:
        print(f"Erro: Faltam dados na camada Silver para as sub-bacias {missing_subbasins} da estação {station_str}!")
        exit(1)

    print(f"Processando posto {station_str}...")

    # 2. Remover agrupamento diário espacial (manter registros individuais por sub-bacia)
    # Não há mais média espacial. Mantemos o df_era5 com todas as sub-bacias intactas.
    print(f"Mantendo {len(subbasin_list)} sub-bacias individuais para o posto {station_str}...")

    # 3. Verificar se o posto existe no arquivo de vazões
    if station_str not in df_vazao.columns:
        print(f"Erro: Posto {station_str} não encontrado no arquivo de vazão.")
        exit(1)

    # 4. Criar as colunas de vazão futura (Look-ahead D0 a D30) para esta estação
    print(f"Gerando colunas de vazão futura (D0 a D30) para o posto {station_str}...")
    vazao_station = df_vazao[['Data', station_str]].copy()
    vazao_station = vazao_station.rename(columns={station_str: 'Vazao'})
    
    # Criar shifts de D0 a D30
    for i in range(31):
        col_name = f'Vazao_D{i}'
        vazao_station[col_name] = vazao_station['Vazao'].shift(-i)
        
    # Remover coluna 'Vazao' original para manter apenas D0 a D30
    vazao_futura = vazao_station.drop(columns=['Vazao'])

    # 5. Mesclar (Merge) dados meteorológicos de cada sub-bacia com a vazão futura
    print(f"Mesclando dados meteorológicos com a vazão futura para o posto {station_str}...")
    df_final = pd.merge(
        df_era5,
        vazao_futura,
        left_on='day',
        right_on='Data',
        how='inner'
    )
    
    # Remover coluna 'Data' duplicada após o merge
    df_final = df_final.drop(columns=['Data'])

    # 5.5 Ordenar os dados por subbasin_id e day para consistência temporal e espacial
    df_final = df_final.sort_values(by=['subbasin_id', 'day']).reset_index(drop=True)

    # 5.6 Filtrar, ordenar e validar a estrutura final de colunas exigida pelo usuário
    expected_cols = [
        'day', 'subbasin_id', 'latitude', 'longitude', 'u10_mean', 'u10_max',
        'u10_min', 'v10_mean', 'v10_max', 'v10_min', 'd2m_mean', 'd2m_max',
        'd2m_min', 't2m_mean', 't2m_max', 't2m_min', 'ssrd_mean', 'ssrd_max',
        'ssrd_min', 'tp_sum', 'tp_max', 'tp_min', 'Vazao_D0', 'Vazao_D1',
        'Vazao_D2', 'Vazao_D3', 'Vazao_D4', 'Vazao_D5', 'Vazao_D6', 'Vazao_D7',
        'Vazao_D8', 'Vazao_D9', 'Vazao_D10', 'Vazao_D11', 'Vazao_D12',
        'Vazao_D13', 'Vazao_D14', 'Vazao_D15', 'Vazao_D16', 'Vazao_D17',
        'Vazao_D18', 'Vazao_D19', 'Vazao_D20', 'Vazao_D21', 'Vazao_D22',
        'Vazao_D23', 'Vazao_D24', 'Vazao_D25', 'Vazao_D26', 'Vazao_D27',
        'Vazao_D28', 'Vazao_D29', 'Vazao_D30'
    ]

    missing_cols = [c for c in expected_cols if c not in df_final.columns]
    if missing_cols:
        print(f"Erro: As seguintes colunas esperadas não estão presentes no DataFrame final: {missing_cols}")
        exit(1)

    df_final = df_final[expected_cols]

    # Validação estrita
    assert list(df_final.columns) == expected_cols, "Erro de validação: A estrutura final das colunas não corresponde exatamente à estrutura exigida!"
    print("Estrutura final validada com sucesso!")

    # 6. Salvar o resultado específico para esta estação
    df_final.to_csv(output_name, index=False)
    
    print(f"Sucesso! Arquivo gerado para posto {station_str}: {output_name}")
    print(f"Estrutura final: {df_final.shape[0]} linhas e {df_final.shape[1]} colunas.")
    print("\nProcessamento finalizado com sucesso.")

if __name__ == "__main__":
    main()
