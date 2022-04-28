# QR-code reader using WeChatCV
## Imports & global variables
import Config

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
DATA_DIRECTORY = Config.Filepath.DATA.value

## Decrypting
def decrypt(laravelEncrypedStringBase64, laravelAppKeyBase64):
    data = json.loads(b64decode(laravelEncrypedStringBase64))
    decrypter = aesDecrypterCBC(b64decode(data['iv']), b64decode(laravelAppKeyBase64) )
    decriptedSerializedMessage = decrypter.decrypt(b64decode(data['value']))
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
    try:
        decoded_message = b64decode(raw_message)
        # Removes unnecessary segments from message (e.g. tags)
        filtered_message = b''.join(decoded_message.split(b",",3)[:3]).replace(b'""',b'","')
        if len(filtered_message) != len(decoded_message):
            filtered_message = filtered_message + b'}'
        message = b64encode(filtered_message)
        key = KEY
        message = decrypt(message,key)
        return_value = message.encode("utf8")
        del decoded_message
        return return_value
    except binascii.Error:
        raise binascii.Error("No QR-code found")


## Reading the QR-code
def process_QR(img,file):
    try:
        content = decode(img)[0].data.decode("utf-8")
    except IndexError:
        raise IndexError
    if content is None:
        image = cv2.imread(f"{DATA_DIRECTORY}/{file}.png")
        content = decode(image)[0].data.decode("utf-8")
    del image
    return content

## Main method (called by API main.py)
def read_file(clean_qr,file):
    try:
        result = process_QR(clean_qr, file)
        qr_content = decrypt_message(result)
        return qr_content
    except IndexError:
        raise IndexError
    except binascii.Error:
        raise binascii.Error