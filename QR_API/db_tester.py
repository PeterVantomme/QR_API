import sqlite3
import os


conn = sqlite3.connect('QR_API\Models\Site\API_DB.db')
cursor = conn.cursor()
print(dict(cursor.execute("SELECT * from userdata;").fetchall()))