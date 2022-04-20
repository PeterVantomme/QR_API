# 
FROM python:3.10.4

# 
WORKDIR /QR_API_0.0.1
# 
COPY QR_API_0.0.1/requirements.txt /QR_API_0.0.1/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /QR_API_0.0.1/requirements.txt

# 
COPY QR_API_0.0.1/$Temp_Documents /QR_API_0.0.1/$Temp_Documents
COPY QR_API_0.0.1/$Temp_Images /QR_API_0.0.1/$Temp_Images
COPY QR_API_0.0.1/$Temp_ImagesForQRReading /QR_API_0.0.1/$Temp_ImagesForQRReading
COPY QR_API_0.0.1/Data /QR_API_0.0.1/Data
COPY QR_API_0.0.1/Models /QR_API_0.0.1/Models
COPY QR_API_0.0.1/QR_Interpreter_ZBAR.py /QR_API_0.0.1/QR_Interpreter_ZBAR.py
COPY QR_API_0.0.1/Transform_Data.py /QR_API_0.0.1/Transform_Data.py

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libzbar0 -y
RUN pip install PyPDF2
CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --max-requests 1000
EXPOSE 80:80