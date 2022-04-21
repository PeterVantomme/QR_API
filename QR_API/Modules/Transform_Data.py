# Process input-pdf to extract QR-code and other pages
## Imports & Globals
import Config
import os
from numpy import array as narray
import fitz
import cv2
import shutil

from PyPDF2  import PdfFileReader, PdfFileWriter

DATA_DIRECTORY = Config.Filepath.DATA_IN.value
IMAGE_DIRECTORY = Config.Filepath.RAW_IMAGES.value
DOCUMENT_DIRECTORY = Config.Filepath.DOCUMENTS.value
QR_IMAGE_DIRECTORY = Config.Filepath.TRANSFORMED_IMAGES.value

## Transform methods
### Transforming the first page to QR-png
def transform_pdf_to_png(filename):
    try:
        PDF = fitz.open(f'{DATA_DIRECTORY}/{filename}.pdf')
        image_list = PDF.get_page_images(0)
        imagefile = fitz.Pixmap(PDF, image_list[0][0]) #First image in document = First page = QR-code
        imagefile.save(f'{IMAGE_DIRECTORY}/{filename}.png')
        del PDF, image_list #deleting variables from memory 
        return None
    except fitz.FileDataError:
        return fitz.FileDataError

### Using opencv transformations to make QR-code more readable for system    
def transform_png(filename):
    image = cv2.imread(f'{IMAGE_DIRECTORY}/{filename}.png')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    kernel = narray([[0, 0, 0],
                    [0, 1, 0],
                    [0, 0, 0]])
    image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

    cross_kernel=cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
    image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)[1]
    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
    image = cv2.threshold(image,200,255,cv2.THRESH_BINARY)[1]
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, cross_kernel)
    kernel = narray([[0, -2, 0],
                    [-2, 12, -2],
                    [0, -2, 0]])
    image = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)
    cv2.imwrite(f"{QR_IMAGE_DIRECTORY}/{filename}.png", image)
    image = cv2.imread(f"{QR_IMAGE_DIRECTORY}/{filename}.png")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=4) 
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel, iterations=4) 
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=4) 
    image = cv2.threshold(image, 192, 255, cv2.THRESH_BINARY)[1]
    kernel = narray([[-1, -1, -1],
                    [-1, 30, -1],
                    [-1, -1, -1]])
    image = cv2.filter2D(src=image, ddepth=5, kernel=kernel)
    cv2.imwrite(f'{QR_IMAGE_DIRECTORY}/{filename}.png',image)
    del image #clearing image variable to help garbage collection

## Cleanup
def cleanup(file):
    os.remove(f'{IMAGE_DIRECTORY}/{file}.png')
    
def remove_first_page(file):    
    #This class removes the first page of the file in order to create a document without the QR-code.
    with open(f'{DATA_DIRECTORY}/{file}.pdf','rb') as f:
        if PdfFileReader(f).getNumPages() > 1:
            information = [2, PdfFileReader(f).getNumPages()]
            pdf_writer = PdfFileWriter()
            start = information[0]
            end = information[1]
            while start<=end:
                pdf_writer.addPage(PdfFileReader(f).getPage(start-1))
                start+=1
            output_filename = f'{DATA_DIRECTORY}/cleared_{file}.pdf'
            with open(output_filename,'wb') as out:
                pdf_writer.write(out)
        else:
            #Document only has one page, thus no need to remove the first page.
            shutil.copyfile(f'{DATA_DIRECTORY}/{file}.pdf', f'{DATA_DIRECTORY}/cleared_{file}.pdf')

## Main method (called by API main.py file)
def transform_file(filename):
    file = filename
    if "cleared" in file:
        cleanup(file)
    else:
        Error = transform_pdf_to_png(file)
        if Error == fitz.FileDataError: return Error
        remove_first_page(file)
        transform_png(file)
            