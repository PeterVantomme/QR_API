# 
FROM python:3.10.4

# 
WORKDIR /
# 
COPY requirements.txt requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 
COPY __Temp_Documents __Temp_Documents
COPY __Temp_Images __Temp_Images
COPY __Temp_Images_for_QRReading __Temp_Images_for_QRReading
COPY __Data __Data
COPY Models Models
COPY Modules Modules
COPY main.py main.py
COPY Config.py Config.py

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libzbar0 -y
RUN pip install PyPDF2
CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --max-requests 1000
EXPOSE 5000:5000