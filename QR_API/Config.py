#This file contains global settings.
from enum import Enum
class Network(Enum):
    PORT = "80"
    ADDRESS = "127.0.0.1"

class Filepath(Enum):
    DATA = "__Temp_Data"
    DATA_OUT_FILENAME = "datafile"
    RAW_IMAGES = "__Temp_Images"
    TRANSFORMED_IMAGES = "__Temp_Images_for_QRReading"
    DOCUMENTS = "__Temp_Documents"
    USER_DB = "Models/Site/API_DB.db"
    PDF_FILE_ADDRESS = "http://127.0.0.1/get_pdf"

class Auth(Enum):
    KEY = b'EDnpXl5oxi9+XHjTUbTwMg98jTeCt4tnJx5LaUtanME='
    AUTH_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    AUTH_TIME = 1 #days
    AUTH_ALG = "HS256"

class Indexer():
    VALUE = 0