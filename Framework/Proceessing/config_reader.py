#Try merging config_reader and excel_reader and rename to Input_reader.py 
import yaml

def read_config(config_path):

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


import pandas as pd

def read_excel_file(excel_path):

    df = pd.read_excel(
        excel_path,
        sheet_name=0
    )

    return df