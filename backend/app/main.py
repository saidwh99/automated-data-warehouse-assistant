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
