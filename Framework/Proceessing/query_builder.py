import re


def validate_table_name(target_table):
    """
    Allow simple table, schema.table, or database.schema.table names.
    """

    pattern = (
        r"^[A-Za-z_][A-Za-z0-9_$]*"
        r"(\.[A-Za-z_][A-Za-z0-9_$]*){0,2}$"
    )

    target_table = str(target_table).strip()

    if not re.fullmatch(pattern, target_table):
        raise ValueError(
            f"Invalid Target_table name: {target_table}"
        )

    return target_table


def quote_column(column_name):
    """
    Safely quote a Snowflake column identifier.
    """

    return '"' + column_name.replace('"', '""') + '"'


def get_table_columns(session, target_table):
    """
    Retrieve column names and data types from Snowflake.
    """

    target_table = validate_table_name(target_table)

    rows = session.sql(
        f"DESCRIBE TABLE {target_table}"
    ).collect()

    columns = []

    for row in rows:
        name = row["name"]
        data_type = row["type"]

        columns.append({
            "name": name,
            "type": data_type.upper()
        })

    if not columns:
        raise ValueError(
            f"No columns found for table: {target_table}"
        )

    return columns


def build_test_query(session, test_case_type, target_table):
    """
    Build SQL queries for TC002, TC003, and TC007.

    TC004, TC005, and TC006 use column metadata
    in main.py rather than executing SQL queries.

    Returns:
        query, metadata
    """

    target_table = validate_table_name(target_table)

    columns = get_table_columns(
        session,
        target_table
    )

    column_names = [
        column["name"] for column in columns
    ]

    quoted_columns = [
        quote_column(name) for name in column_names
    ]

    # --------------------------------------------------
    # TC002: Duplicate complete records
    # --------------------------------------------------
    if test_case_type == "duplicate_full_record":

        group_by = ", ".join(quoted_columns)

        query = f"""
            SELECT
                COUNT(*) AS DUPLICATE_GROUPS,
                COALESCE(
                    SUM(ROW_COUNT - 1),
                    0
                ) AS DUPLICATE_EXCESS_ROWS
            FROM (
                SELECT
                    COUNT(*) AS ROW_COUNT
                FROM {target_table}
                GROUP BY {group_by}
                HAVING COUNT(*) > 1
            ) AS duplicate_rows
        """

        return query, columns

    # --------------------------------------------------
    # TC003: NULL count for every column
    # --------------------------------------------------
    elif test_case_type == "null_count":

        expressions = []

        for index, column in enumerate(column_names):

            quoted = quote_column(column)

            expressions.append(
                f'COUNT_IF({quoted} IS NULL) '
                f'AS "COL_{index}"'
            )

        query = f"""
            SELECT
                {", ".join(expressions)}
            FROM {target_table}
        """

        return query, columns

    # --------------------------------------------------
    # TC007: Special-character validation
    # --------------------------------------------------
    elif test_case_type == "special_character_validation":

        string_columns = [
            column for column in columns
            if any(
                kind in column["type"]
                for kind in [
                    "VARCHAR",
                    "STRING",
                    "TEXT",
                    "CHAR"
                ]
            )
        ]

        if not string_columns:
            return None, []

        expressions = []

        for index, column in enumerate(string_columns):

            quoted = quote_column(column["name"])

            expressions.append(
                f"COUNT_IF("
                f"REGEXP_LIKE("
                f"TO_VARCHAR({quoted}), "
                f"'.*[^A-Za-z0-9 ].*'"
                f")"
                f") AS \"COL_{index}\""
            )

        query = f"""
            SELECT
                {", ".join(expressions)}
            FROM {target_table}
        """

        return query, string_columns

    # --------------------------------------------------
    # TC004, TC005, TC006: Metadata-based checks
    # --------------------------------------------------
    elif test_case_type in (
        "data_type_numeric",
        "data_type_timestamp",
        "data_type_date"
    ):

        return None, columns

    # --------------------------------------------------
    # Unsupported test case
    # --------------------------------------------------
    else:

        raise ValueError(
            f"Unsupported Test_case_type: {test_case_type}"
        )