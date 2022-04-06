from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import shutil
import QR_Interpreter_WeChat
import Transform_Data

app = FastAPI()
FILEPATH_PDF = "Data"

@app.get("/")
async def main():
    content = """
                <body>
                <form action="/uploadfiles" enctype="multipart/form-data" method="post">
                <input name="files" type="file" multiple>
                <input type="submit">
                </form>
                """
    return HTMLResponse(content=content)

@app.post("/uploadfiles")
async def create_upload_files(files: list[UploadFile]):
    try:
        for file in files:
            with open(FILEPATH_PDF+"/"+file.filename, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        response = RedirectResponse(url="/data")
        response.status_code = 302
        return response
    except PermissionError:
        return "Please select files to upload..."

@app.get("/data")
def get_data():
    Transform_Data.transform_all()
    QR_code_message = QR_Interpreter_WeChat.read_all_files()
    return QR_code_message

    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)