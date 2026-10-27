import yaml
import pandas as pd


def read_config(config_path):
    """
    Read the YAML configuration file.
    """
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(
            "Invalid configuration file. Expected a YAML dictionary."
        )

    return config


def read_excel_file(excel_path):
    """
    Read the Excel test-case input file.
    """
    df = pd.read_excel(
        excel_path,
        sheet_name=0
    )

    return df