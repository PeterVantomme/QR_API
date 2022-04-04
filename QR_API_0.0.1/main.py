from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import base64
import QR_Interpreter_WeChat
import Transform_Data
import Config


app = FastAPI()
async def parse_body(request: Request):
    data: bytes = await request.body()
    return data

@app.get("/home")
def get_home():
    print('hi')
    return '<html><body><h1>"Hello world"</h1></body></html>'

@app.post("/data")
async def parse_input(data: bytes = Depends(parse_body)):
    data = base64.b64decode(data)
    file = open(f'{FILEPATH_PDF}/datafile.pdf', 'wb')
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
    FILEPATH_PDF = "Data"
    uvicorn.run(app, host="127.0.0.1", port=80)

