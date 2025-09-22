import subprocess
import sys

scripts = [
    ("Join espacial meteo-subbacia", "scripts/join_meteo_subbasin.py"),
    ("Agregação mensal vazão", "scripts/aggregate_vazao_mensal.py"),
    ("Join meteo+vazão", "scripts/join_meteo_vazao.py"),
    ("Shift temporal (vazão mês seguinte)", "scripts/shift_meteo_vazao.py"),
    ("Split por estação", "scripts/split_meteo_vazao_by_station.py"),
    ("Check split por estação", "scripts/check_split_by_station.py"),
    ("Stats split por estação", "scripts/stats_split_by_station.py"),
    ("Check arquivos por_estacao vs planilha de vazão", "scripts/check_por_estacao_vs_vazao.py"),
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
    for label, path in scripts:
        run_script(label, path)
    print("\nPipeline completo com sucesso!")
