from database.connection import get_connection, close_connection


def execute_select_query(query: str):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(query)

        column_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append(dict(zip(column_names, row)))

        return results

    except Exception as error:
        print(f"Query execution failed: {error}")
        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            close_connection(connection)