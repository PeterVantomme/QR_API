# QR-code reader - WeChat OpenCV
## Imports & global variables
from datetime import datetime
startTime = datetime.now()

#QR-scanning - WECHAT
import cv2
import os
import shutil
#Decryption
import base64
import json
from Cryptodome.Cipher import AES
from phpserialize import loads

KEY = b'EDnpXl5oxi9+XHjTUbTwMg98jTeCt4tnJx5LaUtanME='
QR_DIRECTORY = 'Benchmarking/$Temp_Images_for_QRReading'

DETECTOR_PT_PATH = 'Benchmarking/Models/WeChat/detect.prototxt'
SR_PT_PATH = 'Benchmarking/Models/WeChat/sr.prototxt'
DETECTOR_CAFFE_PATH = 'Benchmarking/Models/WeChat/detect.caffemodel'
SR_CAFFE_PATH = 'Benchmarking/Models/WeChat/sr.caffemodel'

RED = (0,0,255)
GREEN = (0,255,0)
BLUE = (255,0,0)
YELLOW = (0,255,255)
# Font.
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONTSCALE = 0.8
UNPAD = lambda s: s[:-ord(s[len(s) - 1:])]

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

def cleanup(image_filename):
    os.remove(f'{QR_DIRECTORY}/{image_filename}')

def read_all_files():
    # Instantiëren van OpenCV QRCODE detector
    decrypted_QR_Replies = {}
    for image in os.listdir(QR_DIRECTORY):
        try:
            img = cv2.imread(f"{QR_DIRECTORY}/{image}")
            result = process_QR(img).encode("utf8")
            return_value = decrypt_message(result)
            decrypted_QR_Replies[image]=return_value
            cleanup(image)
        except FileNotFoundError:
            print("A configuration or image file could not be found, please check the file structure's integrity...")
            continue
        except ValueError:
            print("The QR-code is too damaged to be read or the key has been changed...")
            continue
    
    return decrypted_QR_Replies