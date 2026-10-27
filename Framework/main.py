from Processing.Input_reader import read_config, read_excel_file
from Environment_Config.Connection_setup import create_session
from Processing.metadata_processing import validate_metadata
from Processing.query_builder import build_test_query


# =====================================================
# READ CONFIGURATION
# =====================================================

config = read_config(
    "Environment_Config/Env_Config.yaml"
)

print("\nConfiguration read Successfully")


# =====================================================
# CREATE SNOWFLAKE SESSION
# =====================================================

try:
    session = create_session(config)
    print("Snowflake Connection Successful")

except Exception as error:
    print(
        "Unable to connect to Snowflake.\n"
        "Please verify account, user, password and role."
    )
    print("Error Details:", error)
    raise SystemExit(1)


# =====================================================
# MAIN EXECUTION
# =====================================================

try:

    # -------------------------------------------------
    # READ EXCEL FILE
    # -------------------------------------------------

    excel_path = config["files"]["User_Testcases"]

    df = read_excel_file(excel_path)

    print("Excel File Read Successfully")


    # -------------------------------------------------
    # VALIDATE METADATA
    # -------------------------------------------------

    validation_status = validate_metadata(df)

    print(
        "Metadata Validation Status:",
        validation_status
    )

    if not validation_status:
        raise ValueError(
            "Metadata validation failed. "
            "Test execution stopped."
        )


    # -------------------------------------------------
    # SUPPORTED TEST CASES
    # -------------------------------------------------

    supported_tests = {
        "TC002": "duplicate_full_record",
        "TC003": "null_count",
        "TC004": "data_type_numeric",
        "TC005": "data_type_timestamp",
        "TC006": "data_type_date",
        "TC007": "special_character_validation"
    }


    # -------------------------------------------------
    # EXECUTE TEST CASES
    # -------------------------------------------------

    for _, row in df.iterrows():

        test_case_id = str(
            row["Test_case_id"]
        ).strip()

        test_case_type = str(
            row["Test_case_type"]
        ).strip()

        target_table = str(
            row["Target_table"]
        ).strip()

        is_required = str(
            row["Is_required"]
        ).strip().upper()


        # ---------------------------------------------
        # PROCESS TC002 TO TC007 ONLY
        # ---------------------------------------------

        if test_case_id not in supported_tests:
            continue


        # ---------------------------------------------
        # VALIDATE TEST CASE TYPE
        # ---------------------------------------------

        expected_type = supported_tests[test_case_id]

        if test_case_type != expected_type:

            print(
                f"\nSkipping {test_case_id}: "
                f"Expected '{expected_type}', "
                f"received '{test_case_type}'."
            )

            continue


        # ---------------------------------------------
        # CHECK Is_required
        # ---------------------------------------------

        if is_required != "Y":

            print(
                f"\nSkipping {test_case_id}: "
                "Is_required is not Y."
            )

            continue


        # ---------------------------------------------
        # DISPLAY TEST CASE INFORMATION
        # ---------------------------------------------

        print("\n" + "=" * 50)

        print("Executing Test Case:", test_case_id)
        print("Test Type:", test_case_type)
        print("Target Table:", target_table)
        print("Is Required:", is_required)

        print("=" * 50)


        try:

            # -----------------------------------------
            # BUILD QUERY AND RETRIEVE TABLE METADATA
            # -----------------------------------------

            query, metadata = build_test_query(
                session,
                test_case_type,
                target_table
            )


            # -----------------------------------------
            # TC004: NUMERIC DATA TYPE CHECK
            # -----------------------------------------

            if test_case_id == "TC004":

                numeric_types = (
                    "NUMBER",
                    "NUMERIC",
                    "DECIMAL",
                    "INT",
                    "INTEGER",
                    "FLOAT",
                    "DOUBLE",
                    "REAL"
                )

                matches = [
                    column["name"]
                    for column in metadata
                    if any(
                        data_type in column["type"]
                        for data_type in numeric_types
                    )
                ]

                if matches:

                    print("Result: PASS")

                    print(
                        "Numeric columns:",
                        ", ".join(matches)
                    )

                else:

                    print("Result: FAIL")
                    print("No numeric columns found.")

                continue


            # -----------------------------------------
            # TC005: TIMESTAMP DATA TYPE CHECK
            # -----------------------------------------

            if test_case_id == "TC005":

                matches = [
                    column["name"]
                    for column in metadata
                    if "TIMESTAMP" in column["type"]
                ]

                if matches:

                    print("Result: PASS")

                    print(
                        "Timestamp columns:",
                        ", ".join(matches)
                    )

                else:

                    print("Result: FAIL")
                    print("No timestamp columns found.")

                continue


            # -----------------------------------------
            # TC006: DATE DATA TYPE CHECK
            # -----------------------------------------

            if test_case_id == "TC006":

                matches = [
                    column["name"]
                    for column in metadata
                    if column["type"].strip() == "DATE"
                ]

                if matches:

                    print("Result: PASS")

                    print(
                        "Date columns:",
                        ", ".join(matches)
                    )

                else:

                    print("Result: FAIL")
                    print("No DATE columns found.")

                continue


            # -----------------------------------------
            # TC007: NO STRING COLUMNS
            # -----------------------------------------

            if (
                test_case_id == "TC007"
                and query is None
            ):

                print("Result: PASS")

                print(
                    "No string columns found to validate."
                )

                continue


            # -----------------------------------------
            # EXECUTE SQL QUERY
            # -----------------------------------------

            result = session.sql(query).collect()


            # -----------------------------------------
            # TC002: DUPLICATE FULL RECORD CHECK
            # -----------------------------------------

            if test_case_id == "TC002":

                duplicate_groups = int(
                    result[0]["DUPLICATE_GROUPS"] or 0
                )

                duplicate_excess_rows = int(
                    result[0]["DUPLICATE_EXCESS_ROWS"] or 0
                )

                print(
                    "Duplicate Groups:",
                    duplicate_groups
                )

                print(
                    "Duplicate Excess Rows:",
                    duplicate_excess_rows
                )

                if duplicate_excess_rows == 0:

                    print("Result: PASS")

                    print(
                        "No duplicate complete rows found."
                    )

                else:

                    print("Result: FAIL")

                    print(
                        "Duplicate complete rows detected."
                    )


            # -----------------------------------------
            # TC003: NULL COUNT CHECK
            # -----------------------------------------

            elif test_case_id == "TC003":

                row_result = result[0]
                total_nulls = 0

                for column_index, column in enumerate(metadata):

                    alias = f"COL_{column_index}"

                    null_count = int(
                        row_result[alias] or 0
                    )

                    total_nulls += null_count

                    print(
                        f"{column['name']}: "
                        f"{null_count} NULL values"
                    )

                print(
                    "Total NULL Values:",
                    total_nulls
                )

                if total_nulls == 0:

                    print("Result: PASS")

                else:

                    print("Result: FAIL")


            # -----------------------------------------
            # TC007: SPECIAL CHARACTER CHECK
            # -----------------------------------------

            elif test_case_id == "TC007":

                row_result = result[0]
                total_flagged = 0

                for column_index, column in enumerate(metadata):

                    alias = f"COL_{column_index}"

                    flagged_count = int(
                        row_result[alias] or 0
                    )

                    total_flagged += flagged_count

                    print(
                        f"{column['name']}: "
                        f"{flagged_count} rows flagged"
                    )

                print(
                    "Total flagged rows across columns:",
                    total_flagged
                )

                if total_flagged == 0:

                    print("Result: PASS")

                else:

                    print("Result: FAIL")


        except Exception as test_error:

            print("Result: ERROR")
            print("Error Details:", test_error)


finally:

    # =================================================
    # CLOSE SNOWFLAKE SESSION
    # =================================================

    session.close()

    print("\nSnowflake Session Closed")