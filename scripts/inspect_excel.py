import pandas as pd

file_path = "/Users/vinicius/Documents/ufrj-hydrosense-data/data/PtsLight_VazaoObs_1998_2025.xlsx"

try:
    xl = pd.ExcelFile(file_path)
    print("Sheets in excel:", xl.sheet_names)
    
    print("\n--- SHEET: Coordenadas_FLU ---")
    df_flu = pd.read_excel(file_path, sheet_name='Coordenadas_FLU')
    print(df_flu.to_string())

    print("\n--- SHEET: Subbacias ---")
    df_sub = pd.read_excel(file_path, sheet_name='Subbacias')
    print(df_sub.to_string())

    for sheet in ['Coordenadas_SANTACECILIA', 'COORDENADAS_PIRAI']:
        print(f"\n--- SHEET: {sheet} ---")
        df = pd.read_excel(file_path, sheet_name=sheet)
        print("Columns:", df.columns.tolist())
        print("Shape:", df.shape)
        print("Lat range:", df['Lat'].min(), "to", df['Lat'].max())
        print("Lon range:", df['Lon'].min(), "to", df['Lon'].max())
        print("First 5 entries:")
        print(df.head().to_string())

except Exception as e:
    print("Error reading excel file:", e)
