import base64
from http.client import CONFLICT
import json
from datetime import timedelta
from os import access

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

import Config
import QR_Interpreter_WeChat
import Transform_Data
from Models.Site.Token import TokenData
from Models.Site.User import Authorised_users
from Security import Security as sec

ACCESS_TOKEN_EXPIRE_DAYS = Config.Auth.AUTH_TIME.value
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
FILENAME = Config.Filepath.DATA_OUT_FILENAME.value
app = FastAPI()

#Byte body handler
async def parse_body(request: Request):
    data: bytes = await request.body()
    return data

#Security handler
async def get_current_user(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="401 - Could not validate credentials - Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Config.Auth.AUTH_KEY.value, algorithms=Config.Auth.AUTH_ALG.value)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except FileExistsError:
        print("no")
    except JWTError:
        raise credentials_exception
    user = sec.get_user(Authorised_users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def get_home():
    return HTMLResponse('<html><body><h3>Welcome to the QR-API, there is no GUI for this so use requests only. (/docs for info) </h3></body></html>', 200)

@app.post("/token")
async def login_for_access_token(data: bytes = Depends(parse_body)):
    credentials = base64.b64decode(data.decode("utf8"))
    credentials = json.loads(credentials.decode("utf8").replace("\\","").replace('"{',"{").replace('}"',"}")) #Dict gets malformed during transfer for some reason
    security = sec(app, oauth2_scheme, pwd_context)
    user = security.authenticate_user(Authorised_users, credentials.get("username"), credentials.get("password"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 - Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    return access_token

@app.post("/data/{token}")
async def parse_input(token, data: bytes = Depends(parse_body)):
    user = await get_current_user(token)
    filename = FILENAME+str(Config.Indexer.VALUE+1)
    if user != None:
        data = base64.b64decode(data)
        with open(f'{Config.Filepath.DATA_IN.value}/{filename}.pdf', 'wb') as file:
            file.write(data)
        Config.Indexer.VALUE += 1 #Increment file-index
        response = RedirectResponse(f"/data/process/{token}/{filename}",302)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 - Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/data/process/{token}/{filename}")
async def get_data(token,filename):
    user = await get_current_user(token)
    if user != None:
        Transform_Data.transform_file(filename)
        QR_code_message = QR_Interpreter_WeChat.read_file(filename)
        return QR_code_message
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 - Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"},
        )

if __name__ == "__main__":
    app = FastAPI()
