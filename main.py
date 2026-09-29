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
# EXECUTE ONE TEST CASE
# =====================================================

for index, row in df.iterrows():

    test_case_id = str(
        row["Test_case_id"]
    ).strip()

    test_case_type = str(
        row["Test_case_type"]
    ).strip()

    source_table = str(
        row["Source_table"]
    ).strip()

    target_table = str(
        row["Target_table"]
    ).strip()

    is_required = str(
        row["Is_required"]
    ).strip().upper()

    # ---------------------------------------------
    # Execute only TC011
    # ---------------------------------------------

    if test_case_id != "TC011":
        continue

    if is_required != "Y":
        continue

    print("\n==========================================")
    print("Executing Test Case:", test_case_id)
    print("Test Type:", test_case_type)
    print("Source Table:", source_table)
    print("Target Table:", target_table)
    print("==========================================")

    # ---------------------------------------------
    # BUILD QUERIES
    # ---------------------------------------------

    source_query, target_query = build_query(
        test_case_type,
        source_table,
        target_table
    )

    print("\nSource Query:")
    print(source_query)

    print("Target Query:")
    print(target_query)

    # ---------------------------------------------
    # EXECUTE SOURCE QUERY
    # ---------------------------------------------

    source_result = session.sql(
        source_query
    ).collect()

    source_count = source_result[0]["SOURCE_COUNT"]

    # ---------------------------------------------
    # EXECUTE TARGET QUERY
    # ---------------------------------------------

    target_result = session.sql(
        target_query
    ).collect()

    target_count = target_result[0]["TARGET_COUNT"]

    print("\nSource Count:", source_count)
    print("Target Count:", target_count)

    # ---------------------------------------------
    # COMPARE RESULTS
    # ---------------------------------------------

    if source_count == target_count:

        print(
            f"\n✓ {test_case_id} PASSED"
        )

    else:

        print(
            f"\n✗ {test_case_id} FAILED"
        )


# =====================================================
# CLOSE SESSION
# =====================================================

session.close()

print("\nSnowflake Session Closed")