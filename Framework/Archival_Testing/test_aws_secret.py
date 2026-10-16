import json
import boto3

REGION = "ap-southeast-1"
SECRET_NAME = "ut-framework/snowflake/credentials"


def retrieve_secret():
    client = boto3.client(
        "secretsmanager",
        region_name=REGION
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
            f"Missing or empty secret fields: {', '.join(missing_keys)}"
        )

    print("AWS Secrets Manager connection successful.")
    print("Secret structure validation successful.")
    print("Snowflake credentials were not displayed.")


if __name__ == "__main__":
    retrieve_secret()