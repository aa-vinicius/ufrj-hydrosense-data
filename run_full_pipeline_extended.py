import subprocess
import sys

# Pipeline original (mantido para compatibilidade)
original_scripts = [
    ("Join espacial meteo-subbacia", "scripts/join_meteo_subbasin.py"),
    ("Agregação mensal vazão", "scripts/aggregate_vazao_mensal.py"),
    ("Join meteo+vazão", "scripts/join_meteo_vazao.py"),
    ("Shift temporal (vazão mês seguinte)", "scripts/shift_meteo_vazao.py"),
    ("Split por estação", "scripts/split_meteo_vazao_by_station.py"),
    ("Check split por estação", "scripts/check_split_by_station.py"),
    ("Stats split por estação", "scripts/stats_split_by_station.py"),
    ("Check arquivos por_estacao vs planilha de vazão", "scripts/check_por_estacao_vs_vazao.py"),
]

# Pipeline estendido (com valores max/min)
extended_scripts = [
    ("Join meteo+vazão (estendido)", "scripts/join_meteo_vazao_extended.py"),
    ("Shift temporal estendido (vazão mês seguinte)", "scripts/shift_meteo_vazao_extended.py"),
    ("Split por estação (estendido)", "scripts/split_meteo_vazao_by_station_extended.py"),
]

def run_script(label, path):
    print(f"\n=== {label} ===")
    result = subprocess.run([sys.executable, path], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print(f"ERRO na etapa: {label}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    print("=== EXECUTANDO PIPELINE ORIGINAL (COMPATIBILIDADE) ===")
    for label, path in original_scripts:
        run_script(label, path)
    
    print("\n=== EXECUTANDO PIPELINE ESTENDIDO (MAX/MIN) ===")
    for label, path in extended_scripts:
        run_script(label, path)
    
    print("\nPipeline completo com sucesso!")
    print("\nArquivos gerados:")
    print("- Originais (apenas média): data/por_estacao/meteo_vazao_shifted_station_*.csv")
    print("- Estendidos (média, max, min): data/por_estacao/meteo_vazao_shifted_station_*_extended.csv")