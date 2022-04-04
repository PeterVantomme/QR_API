from datetime import timedelta
from http.client import HTTPResponse
import Config
import base64
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Depends, FastAPI, HTTPException, status, Request 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    security = sec(app, oauth2_scheme, pwd_context)
    user = security.authenticate_user(Authorised_users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(sec(app, oauth2_scheme, pwd_context).get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(sec(app, oauth2_scheme, pwd_context).get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.post("/data")
def parse_input(data: bytes = Depends(parse_body)):
    data = base64.b64decode(data)
    file = open(f'{Config.Filepath.DATA_IN.value}/{Config.Filepath.DATA_OUT_FILENAME.value}.pdf', 'wb')
    file.write(data)
    file.close()
    response = RedirectResponse("/process", 302)
    return response

@app.get("/data/process")
def get_data():
    Transform_Data.transform_all()
    QR_code_message = QR_Interpreter_WeChat.read_all_files()
    return QR_code_message

if __name__ == "__main__":
    app = FastAPI()
