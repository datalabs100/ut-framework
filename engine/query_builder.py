def build_query(
    test_case_type,
    source_table,
    target_table
):

    if test_case_type == "row_count":

        source_query = f"""
SELECT COUNT(*) AS SOURCE_COUNT
FROM {source_table}
"""

        target_query = f"""
SELECT COUNT(*) AS TARGET_COUNT
FROM {target_table}
"""

        return source_query, target_query

    else:

        raise Exception(
            f"Unsupported test case type: {test_case_type}"
        )