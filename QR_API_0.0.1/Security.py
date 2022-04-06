import Config
from datetime import datetime, timedelta
import Config
from fastapi import HTTPException
from jose import jwt


class Security():
    def __init__(self, application, auth_scheme, pwd_context):
        self.app = application
        self.SECRET_KEY = Config.Auth.AUTH_KEY.value
        self.ALGORITHM = Config.Auth.AUTH_ALG.value
        self.ACCESS_TOKEN_EXPIRE_DAYS = Config.Auth.AUTH_TIME.value
        self.pwd_context = pwd_context
        self.g_oauth2_scheme = auth_scheme

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def get_user(self, authorised_users, username):
        username_verified =  authorised_users().get().get(username) if username in authorised_users().get().keys() else None
        return username_verified

    def authenticate_user(self, authorised_users, username: str, password: str):
        user = self.get_user(authorised_users, username)
        if user is None:
            raise HTTPException(status_code=400, detail="400 - Incorrect username or password")
        if not self.verify_password(password, user.get('hashed_password')):
            raise HTTPException(status_code=400, detail="400 - Incorrect username or password")
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
