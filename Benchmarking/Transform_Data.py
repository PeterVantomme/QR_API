# Processeren van PDF voor het verkrijgen van een image voor de QR-code
## Imports & Globals
DATA_DIRECTORY = "Data"
IMAGE_DIRECTORY = "$Temp_Images"
DOCUMENT_DIRECTORY = "$Temp_Documents"
QR_IMAGE_DIRECTORY = "$Temp_Images_for_QRReading"

import os
import fitz
import cv2

## Transformaties
def transform_pdf_to_png(filename):
    #Converteren van voorblad naar PNG
    PDF = fitz.open(DATA_DIRECTORY+"/"+filename)
    image_list = PDF.get_page_images(0)
    imagefile = fitz.Pixmap(PDF, image_list[0][0])
    imagefile.save(f'{IMAGE_DIRECTORY}/{filename}.png')
    
def transform_png(filename):
    # Transformeren van afbeelding om QR-code leesbaarder te maken
    image = cv2.imread(IMAGE_DIRECTORY+"/"+filename)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #Image naar greyscale veranderen
    blur = cv2.GaussianBlur(gray, (3,3), 0) #Blurren om ruis te verminderen
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] #Image naar zwart-wit contrast
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3)) #Kernel opbouwen voor het transformeren van de afbeelding
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3) #Kernel zorgt ervoor dat zwarte vlekken in voorgrond verdwijnen. (~fill)
    temp_image = cv2.threshold(close, 0, 255, cv2.THRESH_BINARY_INV)[1] #Afbeelding inverteren zodat QR-code terug leesbaar wordt.

    cv2.imwrite(f'{QR_IMAGE_DIRECTORY}/{filename}',temp_image)
"""    cv2.imshow('blur',blur)
    cv2.imshow('thresh',thresh)
    cv2.imshow('close',close)
    cv2.waitKey(0)"""

def cleanup(file):
    #Schoonmaken van temporary directories
    os.remove(DATA_DIRECTORY+"/"+file) 
    os.remove(IMAGE_DIRECTORY+"/"+file+".png")
    
def transform_all():
    ## Verzamelen van te processeren bestanden
    files = os.listdir(DATA_DIRECTORY)

    if len(files)==0:
        None #No new files: Do nothing
    else:    
        for file in files:
            transform_pdf_to_png(file)
            transform_png(file+".png")
            cleanup(file)

            