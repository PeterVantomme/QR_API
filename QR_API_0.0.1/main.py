from datetime import timedelta
import Config
import json
import base64
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, status, Request 
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from Models.Site.User import User, Authorised_users
from Models.Site.Token import Token
from Security import Security as sec
import Transform_Data
import QR_Interpreter_WeChat

# to get a string like this run:
# openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_DAYS = Config.Auth.AUTH_TIME.value

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

async def parse_body(request: Request):
    data: bytes = await request.body()
    return data

@app.get("/")
def get_home():
    return HTMLResponse('<html><body><h3>Welcome to the QR-API, there is no GUI for this so use requests only. (/docs for info) </h3></body></html>', 200)

@app.post("/token")
async def login_for_access_token(data: bytes = Depends(parse_body)):
    credentials = json.loads(base64.b64decode(data))
    security = sec(app, oauth2_scheme, pwd_context)
    user = security.authenticate_user(Authorised_users, credentials.get("username"), credentials.get("password"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": user.get("username")}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/data/{token}")
async def parse_input(token, data: bytes = Depends(parse_body)):
    token = token
    user: str = Depends(sec(app, oauth2_scheme, pwd_context).get_current_user(token))
    data = base64.b64decode(data)
    with open(f'{Config.Filepath.DATA_IN.value}/{Config.Filepath.DATA_OUT_FILENAME.value}.pdf', 'wb') as file:
        file.write(data)
    response = RedirectResponse("/process", 302, headers={"token":token})
    return user #change to response when debugging is done

@app.get("/data/process/{token}")
def get_data(token):
    token = token
    user: str = Depends(sec(app, oauth2_scheme, pwd_context).get_current_user(token))
    sec(app,oauth2_scheme,pwd_context).get_current_user(token)
    Transform_Data.transform_all()
    QR_code_message = QR_Interpreter_WeChat.read_all_files()
    return QR_code_message

if __name__ == "__main__":
    app = FastAPI()
