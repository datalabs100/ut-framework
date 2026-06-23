from engine.config_reader import read_config
from engine.connection_manager import create_session
from engine.excel_reader import read_excel_file
from engine.metadata_validator import validate_metadata
from engine.query_builder import build_query


# =====================================================
# READ CONFIGURATION
# =====================================================

config = read_config(
    "config/framework_config.yaml"
)

print("\nConfiguration read Successfully")


# =====================================================
# CREATE SNOWFLAKE SESSION
# =====================================================

try:
    session = create_session(config)

    print("Snowflake Connection Successful")

except Exception:

    print(
        "Unable to connect to Snowflake.\n"
        "Please verify account, user, password and role."
    )

    exit()


# =====================================================
# READ EXCEL FILE
# =====================================================

excel_path = config["files"]["excel_path"]

df = read_excel_file(excel_path)

print("Excel File Read Successfully")


# =====================================================
# VALIDATE METADATA
# =====================================================

validation_status = validate_metadata(df)

print("Metadata Validation Status:", validation_status)


# =====================================================
# GENERATE QUERIES
# =====================================================




# =====================================================
# CLOSE SESSION
# =====================================================

session.close()

print("\nSnowflake Session Closed")