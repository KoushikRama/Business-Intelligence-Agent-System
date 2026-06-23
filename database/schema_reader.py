from database.queries import execute_select_query


ALLOWED_TABLES = ["employees", "customers", "orders", "payments"]

CATEGORICAL_COLUMNS = {
    "customers": ["region", "state", "customer_segment"],
    "orders": ["order_status"],
    "payments": ["payment_status", "payment_method", "failure_reason"]
}


def get_database_schema() -> str:

    table_names = "', '".join(ALLOWED_TABLES)

    schema_query = f"""
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name IN ('{table_names}')
    ORDER BY table_name, ordinal_position;
    """

    rows = execute_select_query(schema_query)

    schema = {}

    for row in rows:
        table = row["table_name"]
        column = row["column_name"]
        data_type = row["data_type"]

        if table not in schema:
            schema[table] = []

        column_description = f"- {column}: {data_type}"

        if (
            table in CATEGORICAL_COLUMNS
            and column in CATEGORICAL_COLUMNS[table]
        ):

            values_query = f"""
            SELECT DISTINCT {column}
            FROM {table}
            WHERE {column} IS NOT NULL
            ORDER BY {column};
            """

            values = execute_select_query(values_query)

            distinct_values = [
                str(value[column])
                for value in values
            ]

            if distinct_values:
                column_description += (
                    f"\n  Known values: "
                    + ", ".join(distinct_values)
                )

        schema[table].append(column_description)

    schema_text = ""

    for table, columns in schema.items():

        schema_text += f"Table: {table}\n"
        schema_text += "\n".join(columns)
        schema_text += "\n\n"

    return schema_text