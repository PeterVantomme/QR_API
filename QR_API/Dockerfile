# 
FROM python:3.10.4

# 
WORKDIR /
# 
COPY requirements.txt requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 
COPY __Temp_Data __Temp_Data
COPY Models Models
COPY Modules Modules
COPY main.py main.py
COPY Config.py Config.py

RUN apt-get update
#RUN apt-get install ffmpeg libsm6 libxext6 libzbar0 -y
RUN apt-get install ffmpeg libzbar0 -y
RUN pip install PyPDF2
#Keep workers on 1, otherwise Cleanup will cause errors. (It removes loose variables from memories and old files.)
CMD gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 --max-requests 1000 --threads 4 --loop uvloop
EXPOSE 5000:5000