import sqlite3


def data_select(self, base_name, table_name, column_name, filter):
    conn = sqlite3.connect(base_name)
    cursor = conn.cursor()
    cursor.execute("SELECT "+column_name+"FROM "+table_name+"WHERE "+ filter)
    results = cursor.fetchall()
    conn.close()
    return results

def data_insert(self, base_name, table_name, values):
    conn = sqlite3.connect(base_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO"+table_name+"VALUES ("+values+")")
    conn.commit()

def data_update()