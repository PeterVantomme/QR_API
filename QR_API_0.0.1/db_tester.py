import sqlite3
import os


conn = sqlite3.connect('QR_API_0.0.1\Models\Site\API_DB.db')
cursor = conn.cursor()
print(dict(cursor.execute("SELECT * from userdata;").fetchall()))