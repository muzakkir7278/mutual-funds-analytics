import sqlite3

conn = sqlite3.connect("bluestock_mf.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

print("Tables in database:")
print(tables)

for table in tables:
    table_name = table[0]
    cur.execute("SELECT COUNT(*) FROM " + table_name)
    count = cur.fetchone()[0]
    print(table_name, ":", count, "rows")

conn.close()
