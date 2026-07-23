import sqlite3

connection = sqlite3.connect("compra_facil.db")

cursor = connection.execute(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name;
    """
)

print("Tablas encontradas:\n")

for table in cursor.fetchall():
    print("-", table[0])

connection.close()