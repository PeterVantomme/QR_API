from base64 import b64decode
import binascii
import json


import Config
import Modules.QR_Interpreter_ZBAR as QR_Interpreter_ZBAR
import Modules.Transform_Data as Transform_Data
import fitz

from cryptography.fernet import Fernet
from datetime import timedelta
from fastapi import Depends, FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Security as fastapi_security
from jose import jwt, JWTError
from passlib.context import CryptContext
from Models.Site.Token import TokenData
from Modules.Errors import Error as error_reply
from Models.Site.User import Authorised_users
from Modules.Security import Security as sec
from Modules.Cleanup import Cleanup
import tracemalloc


#Globals
ACCESS_TOKEN_EXPIRE_DAYS = Config.Auth.AUTH_TIME.value
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
http_scheme = HTTPBearer()
security = HTTPBearer()
FILENAME = Config.Filepath.DATA_OUT_FILENAME.value
app = FastAPI()

###########################################################################################################################################################################################################
#                                                                                                                                                                                                         #
#                                                          Helper code                                                                                                                                    #
#                                                                                                                                                                                                         #
###########################################################################################################################################################################################################
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

###########################################################################################################################################################################################################
#                                                                                                                                                                                                         #
#                                                          Requesthandling code                                                                                                                           #
#                                                                                                                                                                                                         #
###########################################################################################################################################################################################################

@app.get("/")
def get_home():
    return HTMLResponse('<html><body><h3>Welcome to the QR-API, there is no GUI for this so use requests only. (/docs for info) </h3></body></html>', 200)

#Method for receiving token, this token is needed for most requests
#Use credentials to login {"username": <username>, "password": <password>}
@app.post("/token", response_class=JSONResponse)
async def login_for_access_token(data: Request):
    tracemalloc.start() 
    credentials = await data.json()
    security = sec(app, oauth2_scheme, pwd_context)
    user = security.authenticate_user(Authorised_users, credentials.get("username"), credentials.get("password"))
    if not user:
        raise error_reply.INVALID_CREDENTIALS.value
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": user}, expires_delta=access_token_expires
    )
    return access_token

#Method for checking credentials and receiving PDF document
#Add token to Authorization header
@app.post("/data/")
async def parse_input(file: UploadFile = File(...), credentials: HTTPAuthorizationCredentials = fastapi_security(http_scheme)):
    data = file
    token = credentials.credentials
    user = await get_current_user(token)
    filename = FILENAME+str(Config.Indexer.VALUE)
    filename_old = FILENAME+str(Config.Indexer.VALUE-1)
    Cleanup(filename_old)
    if user != None:
        try:
            with open(f'{Config.Filepath.DATA.value}/{filename}.pdf', 'wb') as file:
                file.write(await data.read())
            Config.Indexer.VALUE += 1 #Increment file-index
            response = RedirectResponse(f"/data/process/{filename}",302, headers={'Authorization': f'Bearer {token}'})
            return response
        except binascii.Error:
            raise error_reply.ENCODE_ERROR.value
    else:
        raise error_reply.INVALID_CREDENTIALS.value

#Method for returning PDF and handling it's transformations
@app.get("/data/process/{filename}", response_class=JSONResponse)
async def get_data(filename, credentials: HTTPAuthorizationCredentials = fastapi_security(http_scheme)):
    token = credentials.credentials
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        try:
            clean_QR = Transform_Data.transform_file(filename)
            QR_code_message = QR_Interpreter_ZBAR.read_file(clean_QR, filename)
            snapshot = tracemalloc.take_snapshot() 
            return_message = {"filename":filename,
                              filename: QR_code_message,
                              "malloc":[str(stat) for stat in snapshot.statistics('lineno')[:10]]}
            #Temporary code for memory
                    
            return return_message
        except binascii.Error:
            raise error_reply.NO_QR_DETECTED.value #Means that document might not even contain one.
        except IndexError:
            raise error_reply.QR_NOT_FOUND.value #Means that scanner cannot read the QR-code.
        except fitz.FileDataError: 
            raise error_reply.UNREADABLE_FILE_FITZ.value
        except FileNotFoundError:
            raise error_reply.INVALID_FILE.value

@app.get("/get_pdf/{filename}", response_class=FileResponse)
async def get_pdf(filename, credentials: HTTPAuthorizationCredentials = fastapi_security(http_scheme)):
    token = credentials.credentials
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        try:
            return f'{Config.Filepath.DATA.value}/{filename}.pdf'
        except FileNotFoundError:
            raise error_reply.FILE_ALREADY_DOWNLOADED.value
        
###########################################################################################################################################################################################################
#                                                                                                                                                                                                         #
#                                                          Admin methods (users, passwords,...)                                                                                                           #
#                                                                                                                                                                                                         #
###########################################################################################################################################################################################################

#Method for changing password
@app.post("/changepassword/") #Needs a dict with old and new password, encrypted using Fernet as body.
async def change_password(credential_dict: bytes = Depends(parse_body), credentials: HTTPAuthorizationCredentials = fastapi_security(http_scheme)):
    token = credentials.credentials
    creds = json.loads(b64decode(Fernet(Config.Auth.KEY.value).decrypt(credential_dict)))
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        username = jwt.decode(token, Config.Auth.AUTH_KEY.value, algorithms=Config.Auth.AUTH_ALG.value).get("sub")
        Authorised_users().change_password(username, pwd_context.hash(creds.get("new_password")))
    return True

#Method for viewing all users
@app.get("/userlist/")
async def get_user_list(credentials: HTTPAuthorizationCredentials = fastapi_security(http_scheme)):
    token = credentials.credentials
    user = await get_current_user(token)
    if user == None:
        raise error_reply.INVALID_CREDENTIALS.value
    else:
        return Authorised_users().get()

if __name__ == "__main__":
    app = FastAPI()
