import os
import pymysql

# Read schema file
with open('database/schema.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

# Connect without specifying database to create it
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Anchit45',
    port=3306,
    autocommit=True
)

cursor = conn.cursor()

# Split statements and execute them individually
statements = sql_script.split(';')
for statement in statements:
    stmt = statement.strip()
    if stmt:
        try:
            cursor.execute(stmt)
        except Exception as e:
            print(f"Error executing statement: {stmt[:50]}... \nError: {e}")

print("Database schema successfully created!")
cursor.close()
conn.close()
