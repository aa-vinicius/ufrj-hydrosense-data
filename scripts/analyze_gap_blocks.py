import pandas as pd

file_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/silver_vazao/aux_vazao_pts_light.csv"
df = pd.read_csv(file_path)
df['Data'] = pd.to_datetime(df['Data'])

def analyze_gaps_with_zeros(df, col):
    is_gap = df[col].isna() | (df[col] == 0)
    
    total_gaps = is_gap.sum()
    nan_count = df[col].isna().sum()
    zero_count = (df[col] == 0).sum()
    
    if not is_gap.any():
        print(f"\nEstação {col}: Sem gaps (NaN ou zerados).")
        return
        
    gaps = []
    in_gap = False
    start_date = None
    
    for i, row in df.iterrows():
        if is_gap.iloc[i]:
            if not in_gap:
                in_gap = True
                start_date = row['Data']
        else:
            if in_gap:
                in_gap = False
                end_date = df.iloc[i-1]['Data']
                gap_len = (end_date - start_date).days + 1
                gaps.append((start_date, end_date, gap_len))
                
    if in_gap:
        end_date = df.iloc[-1]['Data']
        gap_len = (end_date - start_date).days + 1
        gaps.append((start_date, end_date, gap_len))
        
    print(f"\n--- Gaps na Estação {col} (NaN ou Zerados) ---")
    print(f"Total de dias com gaps: {total_gaps} (NaN: {nan_count}, Zerados: {zero_count})")
    print(f"Número de blocos de gaps: {len(gaps)}")
    
    gaps_df = pd.DataFrame(gaps, columns=['Início', 'Fim', 'Duração (dias)'])
    print(gaps_df.sort_values(by='Duração (dias)', ascending=False).head(10).to_string(index=False))

for station in ['19098', '58350001', '19094', '19097']:
    analyze_gaps_with_zeros(df, station)
