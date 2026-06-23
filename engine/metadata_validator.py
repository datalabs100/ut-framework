def show_template():

    print("\n==========================================")
    print("EXPECTED INPUT TEMPLATE")
    print("==========================================\n")

    print("Columns:\n")

    print(
        "Test_case_id | Test_case_type | "
        "Source_table | Target_table | "
        "Is_required\n"
    )

    print("Expected Test Cases:\n")

    print("TC001 : duplicate_pk")
    print("TC002 : duplicate_full_record")
    print("TC003 : null_count")
    print("TC004 : data_type_numeric")
    print("TC005 : data_type_timestamp")
    print("TC006 : data_type_date")
    print("TC007 : special_character_validation")
    print("TC008 : insert_validation")
    print("TC009 : update_validation")
    print("TC010 : delete_validation")

    print("\nOnly these columns can be modified:")
    print("1. Source_table")
    print("2. Target_table")
    print("3. Is_required")

    print("\nIs_required values:")
    print("Y = Execute Test Case")
    print("N = Ignore Test Case")

    print("\n==========================================\n")


def validate_metadata(df):

    print("\nStarting Metadata Validation...\n")

    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    required_columns = [
        "Test_case_id",
        "Test_case_type",
        "Source_table",
        "Target_table",
        "Is_required"
    ]

    missing_columns = []

    for column in required_columns:

        if column not in df.columns:
            missing_columns.append(column)

    if len(missing_columns) > 0:

        print(
            "\nInput file is corrupted.\n"
            "Mandatory data not available.\n"
            "Please use the original template."
        )

        show_template()

        raise Exception(
            "Missing Columns: "
            + ", ".join(missing_columns)
        )

    print("✓ Required Columns Validation Passed")

    # =====================================================
    # EXPECTED TEMPLATE
    # =====================================================

    expected_template = {
        "TC001": "duplicate_pk",
        "TC002": "duplicate_full_record",
        "TC003": "null_count",
        "TC004": "data_type_numeric",
        "TC005": "data_type_timestamp",
        "TC006": "data_type_date",
        "TC007": "special_character_validation",
        "TC008": "insert_validation",
        "TC009": "update_validation",
        "TC010": "delete_validation"
    }

    # =====================================================
    # DUPLICATE TEST CASE CHECK
    # =====================================================

    duplicate_rows = df[
        df.duplicated(
            subset=["Test_case_id"],
            keep=False
        )
    ]

    if len(duplicate_rows) > 0:

        duplicate_ids = (
            duplicate_rows["Test_case_id"]
            .unique()
            .tolist()
        )

        raise Exception(
            "Duplicate Test_case_id found: "
            + ", ".join(
                map(str, duplicate_ids)
            )
        )

    print("✓ Duplicate Test Case Validation Passed")

    # =====================================================
    # ROW LEVEL VALIDATION
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
        # TEST CASE ID VALIDATION
        # ---------------------------------------------

        if test_case_id not in expected_template:

            print(
                "\nInput file is corrupted.\n"
                "Mandatory data not available.\n"
                "Please use the original template."
            )

            show_template()

            raise Exception(
                f"Invalid Test_case_id: "
                f"{test_case_id}"
            )

        # ---------------------------------------------
        # TEST CASE TYPE VALIDATION
        # ---------------------------------------------

        expected_type = expected_template[
            test_case_id
        ]

        if test_case_type != expected_type:

            print(
                "\nInput file is corrupted.\n"
                "Mandatory data not available.\n"
                "Please use the original template."
            )

            show_template()

            raise Exception(
                f"{test_case_id} should contain "
                f"'{expected_type}'"
            )

        # ---------------------------------------------
        # Y / N VALIDATION
        # ---------------------------------------------

        if is_required not in ["Y", "N"]:

            print(
                "\nInput file is corrupted.\n"
                "Mandatory data not available.\n"
                "Please use the original template."
            )

            show_template()

            raise Exception(
                f"{test_case_id}: "
                f"Is_required should contain "
                f"Y or N only."
            )

        # ---------------------------------------------
        # SOURCE / TARGET VALIDATION
        # ---------------------------------------------

        if is_required == "Y":

            if (
                source_table == ""
                or
                source_table.lower() == "nan"
            ):

                raise Exception(
                    f"{test_case_id}: "
                    f"Source_table is blank."
                )

            if (
                target_table == ""
                or
                target_table.lower() == "nan"
            ):

                raise Exception(
                    f"{test_case_id}: "
                    f"Target_table is blank."
                )

    print("✓ Template Validation Passed")
    print("✓ Is_required Validation Passed")
    print("✓ Source/Target Validation Passed")

    print("\nMetadata Validation Successful\n")

    return True