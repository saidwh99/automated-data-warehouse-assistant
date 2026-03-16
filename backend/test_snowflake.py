from dotenv import load_dotenv
import os
import snowflake.connector

load_dotenv()

print("Testing Snowflake connection...")
print("Account:", os.getenv("SNOWFLAKE_ACCOUNT"))
print("User:", os.getenv("SNOWFLAKE_USER"))
print("Warehouse:", os.getenv("SNOWFLAKE_WAREHOUSE"))
print("Database:", os.getenv("SNOWFLAKE_DATABASE"))
print("Schema:", os.getenv("SNOWFLAKE_SCHEMA"))
print("Role:", os.getenv("SNOWFLAKE_ROLE"))

try:
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
    )
    print("Connected to Snowflake successfully")
    conn.close()
except Exception as e:
    print("Connection failed:")
    print(str(e))
