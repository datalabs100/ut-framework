from snowflake.snowpark import Session


def create_session(config):

    connection_parameters = {
        "account": config["snowflake"]["account"],
        "user": config["snowflake"]["user"],
        "password": config["snowflake"]["password"],
        "warehouse": config["snowflake"]["warehouse"],
        "database": config["snowflake"]["database"],
        "schema": config["snowflake"]["schema"],
        "role": config["snowflake"]["role"]
    }

    session = Session.builder.configs(
        connection_parameters
    ).create()

    return session