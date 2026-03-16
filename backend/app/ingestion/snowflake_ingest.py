import os
from dotenv import load_dotenv
import psycopg2
import snowflake.connector

load_dotenv()


def get_pg_connection():
    return psycopg2.connect(
        dbname="dw_assistant",
        user="postgres",
        password="postgres",  # change if needed
        host="localhost",
        port="5432",
    )


def get_snowflake_connection():
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
    database = os.getenv("SNOWFLAKE_DATABASE")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "PUBLIC")
    role = os.getenv("SNOWFLAKE_ROLE")

    missing = []
    values = {
        "SNOWFLAKE_ACCOUNT": account,
        "SNOWFLAKE_USER": user,
        "SNOWFLAKE_PASSWORD": password,
        "SNOWFLAKE_WAREHOUSE": warehouse,
        "SNOWFLAKE_DATABASE": database,
        "SNOWFLAKE_SCHEMA": schema,
        "SNOWFLAKE_ROLE": role,
    }

    for key, value in values.items():
        if not value:
            missing.append(key)

    if missing:
        raise ValueError(f"Missing Snowflake environment variables: {', '.join(missing)}")

    return snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema,
        role=role,
    )


def fetch_tables():
    conn = get_snowflake_connection()
    cur = conn.cursor()

    try:
        print("Connected to Snowflake for table ingestion.")

        cur.execute("""
            SELECT
                table_catalog,
                table_schema,
                table_name,
                table_type,
                comment
            FROM information_schema.tables
            ORDER BY table_schema, table_name
        """)

        rows = cur.fetchall()
        print(f"Fetched {len(rows)} tables from Snowflake.")
        return rows

    finally:
        cur.close()
        conn.close()


def fetch_columns():
    conn = get_snowflake_connection()
    cur = conn.cursor()

    try:
        print("Connected to Snowflake for column ingestion.")

        cur.execute("""
            SELECT
                table_catalog,
                table_schema,
                table_name,
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns
            ORDER BY table_schema, table_name, ordinal_position
        """)

        rows = cur.fetchall()
        print(f"Fetched {len(rows)} columns from Snowflake.")
        return rows

    finally:
        cur.close()
        conn.close()


def load_tables_into_postgres(rows):
    conn = get_pg_connection()
    cur = conn.cursor()

    try:
        print("Connected to PostgreSQL for table load.")

        cur.execute("DELETE FROM warehouse_tables WHERE owner = %s", ("SNOWFLAKE",))

        insert_sql = """
        INSERT INTO warehouse_tables
        (database_name, schema_name, table_name, table_type, description, owner)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        for row in rows:
            cur.execute(
                insert_sql,
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    "SNOWFLAKE",
                ),
            )

        conn.commit()
        print(f"Loaded {len(rows)} tables into PostgreSQL.")

    finally:
        cur.close()
        conn.close()


def load_columns_into_postgres(rows):
    conn = get_pg_connection()
    cur = conn.cursor()

    try:
        print("Connected to PostgreSQL for column load.")

        cur.execute("DELETE FROM warehouse_columns WHERE owner = %s", ("SNOWFLAKE",))

        insert_sql = """
        INSERT INTO warehouse_columns
        (database_name, schema_name, table_name, column_name, data_type, is_nullable, owner)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        for row in rows:
            cur.execute(
                insert_sql,
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    "SNOWFLAKE",
                ),
            )

        conn.commit()
        print(f"Loaded {len(rows)} columns into PostgreSQL.")

    finally:
        cur.close()
        conn.close()


def main():
    print("Starting Snowflake metadata ingestion...")

    table_rows = fetch_tables()
    column_rows = fetch_columns()

    if table_rows:
        load_tables_into_postgres(table_rows)
    else:
        print("No tables found in Snowflake.")

    if column_rows:
        load_columns_into_postgres(column_rows)
    else:
        print("No columns found in Snowflake.")

    print("Snowflake ingestion completed successfully.")


if __name__ == "__main__":
    main()
