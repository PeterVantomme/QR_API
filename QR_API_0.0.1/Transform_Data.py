# Process input-pdf to extract QR-code and other pages
## Imports & Globals
import Config
import os
import fitz
import cv2
from PyPDF2  import PdfFileReader, PdfFileWriter

DATA_DIRECTORY = Config.Filepath.DATA_IN.value
IMAGE_DIRECTORY = Config.Filepath.RAW_IMAGES.value
DOCUMENT_DIRECTORY = Config.Filepath.DOCUMENTS.value
QR_IMAGE_DIRECTORY = Config.Filepath.TRANSFORMED_IMAGES.value

## Transform methods
### Transforming the first page to QR-png
def transform_pdf_to_png(filename):
    PDF = fitz.open(f'{DATA_DIRECTORY}/{filename}.pdf')
    image_list = PDF.get_page_images(0)
    imagefile = fitz.Pixmap(PDF, image_list[0][0]) #First image in document = First page = QR-code
    imagefile.save(f'{IMAGE_DIRECTORY}/{filename}.png')

### Using opencv transformations to make QR-code more readable for system    
def transform_png(filename):
    image = cv2.imread(f'{IMAGE_DIRECTORY}/{filename}.png')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (11,11), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    close = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=5) 
    temp_image = cv2.threshold(close, 0, 255, cv2.THRESH_BINARY_INV)[1]

    cv2.imwrite(f'{QR_IMAGE_DIRECTORY}/{filename}.png',temp_image)

## Cleanup
def cleanup(file):
    os.remove(f'{IMAGE_DIRECTORY}/{file}.png')
    
def remove_first_page(file):    
    #This class removes the first page of the file in order to create a document without the QR-code.
    with open(f'{DATA_DIRECTORY}/{file}.pdf','rb') as f:
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

## Main method (called by API main.py file)
def transform_file(filename):
    file = filename
    if "cleared" in file:
        cleanup(file)
    else:
        transform_pdf_to_png(file)
        remove_first_page(file)
        transform_png(file)
        cleanup(file)

            