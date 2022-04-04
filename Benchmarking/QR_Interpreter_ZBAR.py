# QR-code reader - ZBAR
## Imports & global variables
from datetime import datetime
startTime = datetime.now()

#QR-scanning - ZBAR
import cv2
from pyzbar.pyzbar import decode
import os

#Decryption
import base64
import json
import base64
import json
from Cryptodome.Cipher import AES
from phpserialize import loads

KEY = b'EDnpXl5oxi9+XHjTUbTwMg98jTeCt4tnJx5LaUtanME='
QR_DIRECTORY = 'Benchmarking/$Temp_Images_for_QRReading'

## Decrypter
def process_QR(img):
    data = decode(img)
    message = data[0][0]
    return message

## Reader
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
    filtered_message = b''.join(decoded_message.split(b",",3)[:3]).replace(b'""',b'","')
    if len(filtered_message) != len(decoded_message):
        filtered_message = filtered_message + b'}'
    message = base64.b64encode(filtered_message)
    key = KEY
    message = decrypt(message,key)
    return_value = base64.b64encode(message.encode("utf8"))
    return return_value

def read_all_files():
     #Overloopt alle images in de QR_DIRECTORY, hier komen images terecht nadat ze getransformeerd zijn.
    for image in os.listdir(QR_DIRECTORY):
        img = cv2.imread(f"{QR_DIRECTORY}/{image}")
        result = process_QR(img)
        return_value = decrypt_message(result)
        print(return_value)