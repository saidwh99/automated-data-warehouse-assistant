from fastapi import FastAPI
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

app = FastAPI(title="Automated Data Warehouse Assistant")


def get_connection():
    return psycopg2.connect(
        dbname="dw_assistant",
        user="postgres",
        password="postgres",  # change if your password is different
        host="localhost",
        port="5432",
    )


@app.on_event("startup")
def startup():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_tables (
            id SERIAL PRIMARY KEY,
            database_name VARCHAR(255),
            schema_name VARCHAR(255),
            table_name VARCHAR(255),
            table_type VARCHAR(100),
            description TEXT,
            owner VARCHAR(255)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS warehouse_columns (
            id SERIAL PRIMARY KEY,
            database_name VARCHAR(255),
            schema_name VARCHAR(255),
            table_name VARCHAR(255),
            column_name VARCHAR(255),
            data_type VARCHAR(255),
            is_nullable VARCHAR(50),
            owner VARCHAR(255)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def root():
    return {"message": "Automated Data Warehouse Assistant is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/seed")
def seed():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO warehouse_tables
        (database_name, schema_name, table_name, table_type, description, owner)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        "DW",
        "PUBLIC",
        "CUSTOMER_DIM",
        "BASE TABLE",
        "Customer dimension table",
        "SYSTEM"
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Sample metadata inserted"}


@app.get("/tables")
def tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT database_name, schema_name, table_name, table_type, description, owner
        FROM warehouse_tables
        ORDER BY id
    """)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "results": [
            {
                "database_name": r[0],
                "schema_name": r[1],
                "table_name": r[2],
                "table_type": r[3],
                "description": r[4],
                "owner": r[5],
            }
            for r in rows
        ]
    }

@app.get("/tables/search")
def search_tables(q: str):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT database_name, schema_name, table_name, table_type, description, owner
    FROM warehouse_tables
    WHERE LOWER(table_name) LIKE LOWER(%s)
       OR LOWER(schema_name) LIKE LOWER(%s)
    ORDER BY table_name
    """

    cur.execute(query, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "query": q,
        "results": [
            {
                "database_name": r[0],
                "schema_name": r[1],
                "table_name": r[2],
                "table_type": r[3],
                "description": r[4],
                "owner": r[5],
            }
            for r in rows
        ]
    }
@app.get("/columns")
def columns():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT database_name, schema_name, table_name, column_name, data_type, is_nullable, owner
        FROM warehouse_columns
        ORDER BY table_name, column_name
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "results": [
            {
                "database_name": r[0],
                "schema_name": r[1],
                "table_name": r[2],
                "column_name": r[3],
                "data_type": r[4],
                "is_nullable": r[5],
                "owner": r[6],
            }
            for r in rows
        ]
    }


@app.get("/columns/search")
def search_columns(q: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT database_name, schema_name, table_name, column_name, data_type, is_nullable, owner
        FROM warehouse_columns
        WHERE LOWER(column_name) LIKE LOWER(%s)
           OR LOWER(table_name) LIKE LOWER(%s)
        ORDER BY table_name, column_name
    """, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "query": q,
        "results": [
            {
                "database_name": r[0],
                "schema_name": r[1],
                "table_name": r[2],
                "column_name": r[3],
                "data_type": r[4],
                "is_nullable": r[5],
                "owner": r[6],
            }
            for r in rows
        ]
    }
@app.get("/table-details")
def table_details(table_name: str):
    conn = get_connection()
    cur = conn.cursor()

    try:

        # fetch table info
        cur.execute("""
            SELECT database_name, schema_name, table_name, table_type, description, owner
            FROM warehouse_tables
            WHERE LOWER(table_name) = LOWER(%s)
        """, (table_name,))
        
        table = cur.fetchone()

        if not table:
            return {"error": "Table not found"}

        # fetch columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM warehouse_columns
            WHERE LOWER(table_name) = LOWER(%s)
            ORDER BY column_name
        """, (table_name,))

        columns = cur.fetchall()

        return {
            "table": {
                "database": table[0],
                "schema": table[1],
                "table_name": table[2],
                "type": table[3],
                "description": table[4],
                "owner": table[5],
            },
            "columns": [
                {
                    "column_name": c[0],
                    "data_type": c[1],
                    "nullable": c[2]
                }
                for c in columns
            ]
        }

    finally:
        cur.close()
        conn.close()