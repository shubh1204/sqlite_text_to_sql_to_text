import sqlite3


def fetch_data_as_markdown(db_path, table_name):
    """
    Fetch data from the SQLite database and return it as a Markdown table.

    Args:
        db_path (str): Path to the SQLite database file.
        table_name (str): Name of the table to fetch data from.

    Returns:
        str: Data formatted as a Markdown table.
    """
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Fetch the table column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]

        # Fetch the table data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Generate the Markdown table
        markdown = f"| {' | '.join(columns)} |\n"
        markdown += f"| {' | '.join(['---' for _ in columns])} |\n"
        for row in rows:
            markdown += f"| {' | '.join(map(str, row))} |\n"

        return markdown

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return ""

    finally:
        # Close the database connection
        conn.close()


def run_query_on_sqlite(db_path, query, params=None):
    """
    Run an SQL query on an SQLite database and return the result as a markdown string.

    Args:
        db_path (str): The path to the SQLite database file.
        query (str): The SQL query to execute.
        params (tuple, optional): Query parameters to safely substitute into the SQL query. Defaults to None.

    Returns:
        str: The query result formatted as a markdown table (for SELECT queries),
             or a status message for non-SELECT queries.
    """
    import sqlite3
    import pandas as pd

    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute the query with optional parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # If it's a SELECT query, fetch and format the result as a markdown table
        if query.strip().upper().startswith("SELECT"):
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            df = pd.DataFrame(rows, columns=columns)
            markdown_result = df.to_markdown(index=False)
            return markdown_result

        # Commit changes for non-SELECT queries and return a status message
        conn.commit()
        return "**Query executed successfully.**"

    except sqlite3.Error as e:
        return f"**An error occurred:** {e}"

    finally:
        if conn:
            conn.close()
