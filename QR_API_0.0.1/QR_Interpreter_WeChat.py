# QR-code reader - WeChat OpenCV
## Imports & global variables
import Config

#QR-scanning - WECHAT
import cv2
import os
import shutil
#Decryption
import base64
import json
from Cryptodome.Cipher import AES
from phpserialize import loads

KEY = Config.Auth.KEY.value
QR_DIRECTORY = Config.Filepath.TRANSFORMED_IMAGES.value
DATA_DIRECTORY = Config.Filepath.DATA_IN.value

DETECTOR_PT_PATH = 'Models/WeChat/detect.prototxt'
SR_PT_PATH = 'Models/WeChat/sr.prototxt'
DETECTOR_CAFFE_PATH = 'Models/WeChat/detect.caffemodel'
SR_CAFFE_PATH = 'Models/WeChat/sr.caffemodel'

## Decrypter
def decrypt(laravelEncrypedStringBase64, laravelAppKeyBase64):
    # Decode from base64 Laravel encrypted string
    dataJson = base64.b64decode(laravelEncrypedStringBase64)
    # Load JSON
    data = json.loads(dataJson)
    # Extract actual encrypted message from JSON (other parts are IV and Signature)
    value =  base64.b64decode(data['value'])
    # Extract Initialization Vector from JSON (required to create an AES decypher)
    iv = base64.b64decode(data['iv'])
    # Decode 
    key = base64.b64decode(laravelAppKeyBase64)  # Laravel KEY comes base64Encoded from .env!
    # Create an AES decypher
    decrypter = aesDecrypterCBC(iv, key)
    # Finally decypher the message
    decriptedSerializedMessage = decrypter.decrypt(value)
    # deserialize message
    try :
        # Attempt to deserialize message incase it was created in Laravel with Crypt::encrypt('Hello world.');
        decriptedMessage = unserialize(decriptedSerializedMessage)
        return str(decriptedMessage)
    except:
        raise Exception("Check you cyphered strings in Laravel using Crypt::encrypt() and NOT Crypt::encryptString()")

def aesDecrypterCBC(iv, _key):
    decrypterAES_CBC = AES.new(key=_key,mode=AES.MODE_CBC,IV=iv)
    return decrypterAES_CBC

def unserialize(serialized):
    return loads(serialized)

def decrypt_message(raw_message):
    decoded_message = base64.b64decode(raw_message)
    # De volgende drie lijnen zorgen dat de "tag" uit de JSON wordt verwijdert aangezien we die niet nodig hebben.
    filtered_message = b''.join(decoded_message.split(b",",3)[:3]).replace(b'""',b'","')
    if len(filtered_message) != len(decoded_message):
        filtered_message = filtered_message + b'}'
    message = base64.b64encode(filtered_message)
    key = KEY
    message = decrypt(message,key)
    return_value = base64.b64encode(message.encode("utf8"))
    return return_value

## Reader
def process_QR(img):
    detector = cv2.wechat_qrcode_WeChatQRCode(DETECTOR_PT_PATH, DETECTOR_CAFFE_PATH, SR_PT_PATH, SR_CAFFE_PATH)
    res,_ = detector.detectAndDecode(img)
    return res[0]

def cleanup():
    for file in os.listdir(QR_DIRECTORY):
        try:
            os.remove(QR_DIRECTORY+"/"+file)
        except PermissionError:
            print("File still in use, can't remove...")
    for file in os.listdir(DATA_DIRECTORY):
        try:
            os.remove(DATA_DIRECTORY+"/"+file)
        except PermissionError:
            print("File still in use, can't remove...")

def read_all_files():
    # Instantiëren van OpenCV QRCODE detector
    img = cv2.imread(f"{QR_DIRECTORY}/{os.listdir(QR_DIRECTORY)[0]}")
    result = process_QR(img).encode("utf8")
    return_value = decrypt_message(result)

    with open(f"{DATA_DIRECTORY}/cleared_datafile.pdf", "rb") as pdf_file:
        encoded = base64.b64encode(pdf_file.read())
    
    decrypted_QR_Replies={"filename" : os.listdir(QR_DIRECTORY)[0],
                          "QR_content" : return_value,
                          "Pages" : encoded}
    cleanup()
    return decrypted_QR_Replies