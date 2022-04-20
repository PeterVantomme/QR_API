from pydantic import BaseModel
import sqlite3
import Config

class User(BaseModel):
    username : str
    enabled: bool

class UserInDB(User):
    hashed_password: str

class Authorised_users():
    def __init__(self):
        self.conn = sqlite3.connect(Config.Filepath.USER_DB.value)
        self.cursor = self.conn.cursor()

    def get(self):
        data = dict(self.cursor.execute("SELECT * FROM userdata;").fetchall())
        self.conn.close()
        return data

    def change_password(self, username, new_password):
        self.cursor.execute("UPDATE userdata SET password_hash = ? WHERE username = ?;",(new_password,username))
        self.conn.commit()
        self.conn.close()