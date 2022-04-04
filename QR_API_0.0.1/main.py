from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import conint
import uvicorn
import base64
import QR_Interpreter_WeChat
import Transform_Data
import Config

app = FastAPI()

async def parse_body(request: Request):
    data: bytes = await request.body()
    return data

@app.get("/")
def get_home():
    return HTMLResponse('<html><body><h3>Welcome to the QR-API, there is no GUI for this so use requests only. (/docs for info) </h3></body></html>', 200)

@app.post("/data")
def parse_input(data: bytes = Depends(parse_body)):
    FILEPATH_PDF = Config.Filepath.DATA_IN.value
    data = base64.b64decode(data)
    file = open(f'{FILEPATH_PDF}/{Config.Filepath.DATA_OUT_FILENAME.value}.pdf', 'wb')
    file.write(data)
    file.close()
    response = RedirectResponse("/process", 302)
    return response

@app.get("/process")
def get_data():
    Transform_Data.transform_all()
    QR_code_message = QR_Interpreter_WeChat.read_all_files()
    return QR_code_message

if __name__ == "__main__":
    app = FastAPI()
