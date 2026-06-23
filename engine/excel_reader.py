import pandas as pd

def read_excel_file(excel_path):

    df = pd.read_excel(
        excel_path,
        sheet_name=0
    )

    return df