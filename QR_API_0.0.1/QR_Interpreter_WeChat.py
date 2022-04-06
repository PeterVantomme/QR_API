# QR-code reader using WeChatCV
## Imports & global variables
import Config

###QR-scanning - WECHAT
import cv2
import os
###Decryption
import base64
import json
from Cryptodome.Cipher import AES
from phpserialize import loads

###Globals
KEY = Config.Auth.KEY.value
QR_DIRECTORY = Config.Filepath.TRANSFORMED_IMAGES.value
DATA_DIRECTORY = Config.Filepath.DATA_IN.value

# Model used by WeChat OpenCV scanner (improves existing opencv model)
DETECTOR_PT_PATH = 'Models/WeChat/detect.prototxt'
SR_PT_PATH = 'Models/WeChat/sr.prototxt'
DETECTOR_CAFFE_PATH = 'Models/WeChat/detect.caffemodel'
SR_CAFFE_PATH = 'Models/WeChat/sr.caffemodel'

## Decrypting
def decrypt(laravelEncrypedStringBase64, laravelAppKeyBase64):
    dataJson = base64.b64decode(laravelEncrypedStringBase64)
    data = json.loads(dataJson)
    value =  base64.b64decode(data['value'])
    iv = base64.b64decode(data['iv'])
    key = base64.b64decode(laravelAppKeyBase64) 
    decrypter = aesDecrypterCBC(iv, key)
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
    # Removes unnecessary segments from message (e.g. tags)
    filtered_message = b''.join(decoded_message.split(b",",3)[:3]).replace(b'""',b'","')
    if len(filtered_message) != len(decoded_message):
        filtered_message = filtered_message + b'}'
    message = base64.b64encode(filtered_message)
    key = KEY
    message = decrypt(message,key)
    return_value = base64.b64encode(message.encode("utf8"))
    return return_value

## Reading the QR-code
def process_QR(img):
    detector = cv2.wechat_qrcode_WeChatQRCode(DETECTOR_PT_PATH, DETECTOR_CAFFE_PATH, SR_PT_PATH, SR_CAFFE_PATH)
    res,_ = detector.detectAndDecode(img)
    return res[0]

def cleanup(filename):
    for file in os.listdir(QR_DIRECTORY):
        try:
            os.remove(QR_DIRECTORY+"/"+file) if filename in file else ""
        except PermissionError:
            print("File still in use, can't remove...")
    for file in os.listdir(DATA_DIRECTORY):
        try:
            os.remove(DATA_DIRECTORY+"/"+file) if filename in file else ""
        except PermissionError:
            print("File still in use, can't remove...")

## Main method (called by API main.py)
def read_file(filename):
    img = cv2.imread(f"{QR_DIRECTORY}/{filename}.png")
    result = process_QR(img).encode("utf8")
    return_value = decrypt_message(result)

    with open(f"{DATA_DIRECTORY}/cleared_{filename}.pdf", "rb") as pdf_file:
        encoded = base64.b64encode(pdf_file.read())
    
    decrypted_QR_Replies={"filename" : filename,
                          "QR_content" : return_value,
                          "Pages" : encoded}
    cleanup(filename)
    return decrypted_QR_Replies