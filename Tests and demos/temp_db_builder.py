import sqlite3
import pandas as pd

conn = sqlite3.connect('API_DB.db')
c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS userdata
          ([username] varchar(32) PRIMARY KEY, [password_hash] varchar(128))
          ''')
c.execute('''
          INSERT INTO userdata (username, password_hash)
          VALUES ("dev", "$2b$12$I0I8oCSOP.nz6.4nyFn9JOk6dYjar9lB3r4Fmuu4VxribHkJRmgZm"),
                ("test", "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW")
          ''')
c.execute('''
          SELECT * FROM userdata
          ''')
conn.commit()

df = pd.DataFrame(c.fetchall(), columns=['username','password_hash'])
print (df)