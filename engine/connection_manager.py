import json
import boto3

from snowflake.snowpark import Session


AWS_REGION = "ap-southeast-1"
SECRET_NAME = "ut-framework/snowflake/credentials"


def get_snowflake_credentials():

    client = boto3.client(
        "secretsmanager",
        region_name=AWS_REGION
    )

    response = client.get_secret_value(
        SecretId=SECRET_NAME
    )

    secret = json.loads(response["SecretString"])

    required_keys = [
        "account",
        "user",
        "password",
        "warehouse",
        "database",
        "schema",
        "role"
    ]

    missing_keys = [
        key for key in required_keys
        if not secret.get(key)
    ]

    if missing_keys:
        raise ValueError(
            f"Missing or empty Snowflake credential fields: "
            f"{', '.join(missing_keys)}"
        )

    return secret


def create_session(config=None):

    credentials = get_snowflake_credentials()

    connection_parameters = {
        "account": credentials["account"],
        "user": credentials["user"],
        "password": credentials["password"],
        "warehouse": credentials["warehouse"],
        "database": credentials["database"],
        "schema": credentials["schema"],
        "role": credentials["role"]
    }

    session = Session.builder.configs(
        connection_parameters
    ).create()

    return session