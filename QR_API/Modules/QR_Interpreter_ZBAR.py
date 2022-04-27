# QR-code reader using WeChatCV
## Imports & global variables
from numpy import dtype
import Config

###QR-scanning - WECHAT
import cv2

###Decryption
from base64 import b64encode, b64decode
import json
from Cryptodome.Cipher import AES
from phpserialize import loads
from pyzbar.pyzbar import decode
import binascii

###Globals
KEY = Config.Auth.KEY.value
QR_DIRECTORY = Config.Filepath.TRANSFORMED_IMAGES.value
DATA_DIRECTORY = Config.Filepath.DATA_IN.value

## Decrypting
def decrypt(laravelEncrypedStringBase64, laravelAppKeyBase64):
    dataJson = b64decode(laravelEncrypedStringBase64)
    data = json.loads(dataJson)
    value =  b64decode(data['value'])
    iv = b64decode(data['iv'])
    key = b64decode(laravelAppKeyBase64) 
    decrypter = aesDecrypterCBC(iv, key)
    decriptedSerializedMessage = decrypter.decrypt(value)
    # deserialize message
    try :
        # Attempt to deserialize message incase it was created in Laravel with Crypt::encrypt('Hello world.');
        decriptedMessage = unserialize(decriptedSerializedMessage)
        del dataJson, data, value, iv, key, decrypter, decriptedSerializedMessage
        return str(decriptedMessage)
    except:
        raise Exception("Check you cyphered strings in Laravel using Crypt::encrypt() and NOT Crypt::encryptString()")

def aesDecrypterCBC(iv, _key):
    decrypterAES_CBC = AES.new(key=_key,mode=AES.MODE_CBC,IV=iv)
    return decrypterAES_CBC

def unserialize(serialized):
    return loads(serialized)

def decrypt_message(raw_message):
    try:
        decoded_message = b64decode(raw_message)
        # Removes unnecessary segments from message (e.g. tags)
        filtered_message = b''.join(decoded_message.split(b",",3)[:3]).replace(b'""',b'","')
        if len(filtered_message) != len(decoded_message):
            filtered_message = filtered_message + b'}'
        message = b64encode(filtered_message)
        key = KEY
        message = decrypt(message,key)
        return_value = b64encode(message.encode("utf8"))
        del decoded_message
        return return_value
    except binascii.Error:
        raise binascii.Error("No QR-code found")


## Reading the QR-code
def process_QR(img):
    try:
        content = decode(img)[0].data.decode("utf-8")
    except IndexError:
        raise IndexError
    return content

## Main method (called by API main.py)
def read_file(filename, clean_qr):
    try:
        img = clean_qr
        result = process_QR(img)
        return_value = decrypt_message(result)

        with open(f"{DATA_DIRECTORY}/cleared_{filename}.pdf", "rb") as pdf_file:
            encoded = b64encode(pdf_file.read())
        
        decrypted_QR_Replies={"filename" : filename,
                            "QR_content" : return_value,
                            "Pages" : encoded}
        return decrypted_QR_Replies
    except IndexError:
        raise IndexError
    except binascii.Error:
        raise binascii.Error