import base64
import binascii
import json

from cryptography.fernet import Fernet
from datetime import timedelta
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

import Config
import QR_Interpreter_ZBAR
import Transform_Data
from Models.Site.Token import TokenData
from Errors import Error as error_reply
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
    credentials_exception = error_reply.INVALID_TOKEN.value
    try:
        payload = jwt.decode(token, Config.Auth.AUTH_KEY.value, algorithms=Config.Auth.AUTH_ALG.value)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        user = sec(app, oauth2_scheme, pwd_context).get_user(Authorised_users, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user
    except FileExistsError:
        raise error_reply.INVALID_FILE.value
    except JWTError:
        raise credentials_exception

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
        raise error_reply.INVALID_CREDENTIALS.value
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    return access_token

@app.post("/data/{token}")
async def parse_input(token, data: bytes = Depends(parse_body)):
    user = await get_current_user(token)
    filename = FILENAME+str(Config.Indexer.VALUE+1)
    if user != None:
        try:
            data = base64.b64decode(data)
            with open(f'{Config.Filepath.DATA_IN.value}/{filename}.pdf', 'wb') as file:
                file.write(data)
            Config.Indexer.VALUE += 1 #Increment file-index
            response = RedirectResponse(f"/data/process/{token}/{filename}",302)
            return response
        except binascii.Error:
            raise error_reply.ENCODE_ERROR.value
    else:
        raise error_reply.INVALID_CREDENTIALS.value

@app.get("/data/process/{token}/{filename}")
async def get_data(token,filename):
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        Error = Transform_Data.transform_file(filename)
        if Error == None:
            QR_code_message = QR_Interpreter_ZBAR.read_file(filename)
            return QR_code_message
        else:
            raise error_reply.UNREADABLE_FILE.value
        
@app.post("/changepassword/{token}") #Needs a dict with old and new encrypted password using Fernet as body.
async def change_password(token, credential_dict: bytes = Depends(parse_body)):
    creds = json.loads(base64.b64decode(Fernet(Config.Auth.KEY.value).decrypt(credential_dict)))
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        username = jwt.decode(token, Config.Auth.AUTH_KEY.value, algorithms=Config.Auth.AUTH_ALG.value).get("sub")
        Authorised_users().change_password(username, pwd_context.hash(creds.get("new_password")))
    return True
        

@app.get("/passhash/{password}")
def get_hashed_pw(password):
    return pwd_context.hash(password)

@app.get("/userlist/{token}")
async def get_user_list(token):
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        return Authorised_users().get()


if __name__ == "__main__":
    app = FastAPI()
