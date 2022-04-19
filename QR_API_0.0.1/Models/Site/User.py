from pydantic import BaseModel
class User(BaseModel):
    username : str
    enabled: bool

class UserInDB(User):
    hashed_password: str

class Authorised_users():
    def __init__(self):
        self.userdict = {
            "dev": {
                "username": "dev",
                "hashed_password": "$2b$12$rOmoIVRsgQ2O5OuFu1sKP.X4adZFB8dQSPJOusAox.6rEM8k9kBau",
            },
            "test":{
                "username": "test",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            }
        }

    def get(self):
        return self.userdict