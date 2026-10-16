def show_template():

    print("\n==========================================")
    print("EXPECTED INPUT TEMPLATE")
    print("==========================================\n")

    print(
        "Test_case_id | Test_case_type | "
        "Target_table | Is_required\n"
    )

    print("Supported Test Cases:\n")

    print("TC002 : duplicate_full_record")
    print("TC003 : null_count")
    print("TC004 : data_type_numeric")
    print("TC005 : data_type_timestamp")
    print("TC006 : data_type_date")
    print("TC007 : special_character_validation")

    print("\nOther Defined Test Cases:\n")

    print("TC001 : duplicate_pk")
    print("TC008 : insert_validation")
    print("TC009 : update_validation")
    print("TC010 : delete_validation")
    print("TC011 : row_count")

    print("\nEditable Columns:")
    print("1. Target_table")
    print("2. Is_required")

    print("\nIs_required Behavior:")
    print("Y / y = Execute Test Case")
    print("Any other value = Skip Test Case")

    print("\n==========================================\n")


def validate_metadata(df):

    print("\nStarting Metadata Validation...\n")

    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    required_columns = [
        "Test_case_id",
        "Test_case_type",
        "Target_table",
        "Is_required"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print(
            "\nInput file is corrupted.\n"
            "Mandatory columns are missing.\n"
            "Please use the original template."
        )

        show_template()

        raise ValueError(
            "Missing Columns: "
            + ", ".join(missing_columns)
        )

    print("✓ Required Columns Validation Passed")

    # =====================================================
    # EXPECTED TEST CASES
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
        "TC010": "delete_validation",
        "TC011": "row_count"
    }

    # =====================================================
    # DUPLICATE TEST CASE ID VALIDATION
    # =====================================================

    normalized_ids = (
        df["Test_case_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    duplicate_mask = normalized_ids.duplicated(keep=False)

    # Ignore blank IDs here; they are handled below.
    duplicate_rows = df[
        duplicate_mask & normalized_ids.ne("")
    ]

    if not duplicate_rows.empty:

        duplicate_ids = (
            normalized_ids[duplicate_mask & normalized_ids.ne("")]
            .unique()
            .tolist()
        )

        raise ValueError(
            "Duplicate Test_case_id found: "
            + ", ".join(duplicate_ids)
        )

    print("✓ Duplicate Test Case Validation Passed")

    # =====================================================
    # ROW-LEVEL VALIDATION
    # =====================================================

    for index, row in df.iterrows():

        excel_row = index + 2

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
        # TEST CASE ID VALIDATION
        # ---------------------------------------------

        if (
            not test_case_id
            or test_case_id.lower() == "nan"
        ):

            raise ValueError(
                f"Excel row {excel_row}: "
                "Test_case_id cannot be blank."
            )

        if test_case_id not in expected_template:

            show_template()

            raise ValueError(
                f"Excel row {excel_row}: "
                f"Invalid Test_case_id: {test_case_id}"
            )

        # ---------------------------------------------
        # TEST CASE TYPE VALIDATION
        # ---------------------------------------------

        if (
            not test_case_type
            or test_case_type.lower() == "nan"
        ):

            raise ValueError(
                f"Excel row {excel_row}: "
                f"Test_case_type is blank for {test_case_id}."
            )

        expected_type = expected_template[test_case_id]

        if test_case_type != expected_type:

            show_template()

            raise ValueError(
                f"Excel row {excel_row}: "
                f"{test_case_id} must have "
                f"Test_case_type '{expected_type}'."
            )

        # ---------------------------------------------
        # IS_REQUIRED HANDLING
        # ---------------------------------------------
        #
        # Only Y/y executes the test.
        #
        # Blank, N, special characters, numbers,
        # or any other value mean SKIP.
        #
        # These values must not cause validation errors.
        # ---------------------------------------------

        if is_required != "Y":
            continue

        # ---------------------------------------------
        # TARGET TABLE VALIDATION
        # ---------------------------------------------

        if (
            not target_table
            or target_table.lower() == "nan"
        ):

            raise ValueError(
                f"Excel row {excel_row}: "
                f"Target_table is blank for {test_case_id}, "
                "which is marked as required."
            )

    # =====================================================
    # VALIDATION SUCCESS
    # =====================================================

    print("✓ Required Columns Validation Passed")
    print("✓ Duplicate Test Case Validation Passed")
    print("✓ Template Validation Passed")
    print("✓ Is_required Validation Passed")
    print("✓ Target_table Validation Passed")

    print("\nMetadata Validation Successful\n")

    return True