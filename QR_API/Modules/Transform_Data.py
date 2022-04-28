# Process input-pdf to extract QR-code and other pages
## Imports & Globals
from pickle import TRUE
import Config
import os
import numpy as np
import fitz
import cv2

DATA_DIRECTORY = Config.Filepath.DATA.value
IMAGE_DIRECTORY = Config.Filepath.RAW_IMAGES.value
DOCUMENT_DIRECTORY = Config.Filepath.DOCUMENTS.value
QR_IMAGE_DIRECTORY = Config.Filepath.TRANSFORMED_IMAGES.value

## Helper zorgt ervoor dat pdf image gelezen kan worden door cv2
def pix2np(pix):
    im = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    im = np.ascontiguousarray(im[...])  # rgb to bgr
    im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
    return im

## Transform methods
### Transforming the first page to QR-png
def transform_pdf_to_png(pdf):
    pix = fitz.Pixmap(pdf, pdf.get_page_images(0)[0][0])  
    im = pix2np(pix)
    return im


### Using opencv transformations to make QR-code more readable for system    
def transform_png(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    kernel = np.array([[0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]])
    image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

    cross_kernel=cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
    image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)[1]
    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
    image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)[1]
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, cross_kernel)
    kernel = np.array([[0, -2, 0],
                    [-2, 12, -2],
                    [0, -2, 0]])
    image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=4) 
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=4) 
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=4) 
    image = cv2.threshold(image, 192, 255, cv2.THRESH_BINARY)[1]
    kernel = np.array([[-1, -1, -1],
                    [-1, 30, -1],
                    [-1, -1, -1]])
    image = cv2.filter2D(src=image, ddepth=5, kernel=kernel)
    return image

## Remove first page
def remove_first_page(file):    
    del file[0]
    return file

## Main method (called by API main.py file)
def transform_file(file):
    try:
        pdf = fitz.open(f'{DATA_DIRECTORY}/{file}.pdf')
        image = transform_pdf_to_png(pdf)
        clean_image = transform_png(image)
        pdf = remove_first_page(pdf)
        if pdf.can_save_incrementally():
            pdf.saveIncr()
        else:
            pdf.save(f'{DATA_DIRECTORY}/{file}.pdf')
            
        return clean_image
    except fitz.FileDataError:
        raise fitz.FileDataError
    except FileNotFoundError:
        raise FileNotFoundError
            