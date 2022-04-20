# 
FROM python:3.10.4

# 
WORKDIR /QR_API
# 
COPY QR_API/requirements.txt /QR_API/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /QR_API/requirements.txt

# 
COPY QR_API/__Temp_Documents /QR_API/__Temp_Documents
COPY QR_API/__Temp_Images /QR_API/__Temp_Images
COPY QR_API/__Temp_Images_for_QRReading /QR_API/__Temp_Images_for_QRReading
COPY QR_API/__Data /QR_API/__Data
COPY QR_API/Models /QR_API/Models
COPY QR_API/Modules /QR_API/Modules
COPY QR_API/main.py /QR_API/main.py
COPY QR_API/Config.py /QR_API/Config.py

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libzbar0 -y
RUN pip install PyPDF2
CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80 --max-requests 1000
EXPOSE 80:80