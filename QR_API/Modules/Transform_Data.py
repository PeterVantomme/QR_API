# Process input-pdf to extract QR-code and other pages
## Imports & Globals
import Config
import numpy as np
import fitz
from cv2 import COLOR_BGR2HSV, COLOR_RGB2GRAY, COLOR_HSV2RGB, COLOR_BGR2RGB, COLOR_RGB2BGR, COLOR_BGR2GRAY, COLOR_GRAY2RGB, MORPH_CLOSE, MORPH_RECT, MORPH_CROSS, MORPH_OPEN, THRESH_BINARY
from cv2 import cvtColor, filter2D, getStructuringElement, threshold, morphologyEx, resize 
DATA_DIRECTORY = Config.Filepath.DATA.value

## Helper zorgt ervoor dat pdf image gelezen kan worden door cv2
def pix2np(pix):
    im = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    im = np.ascontiguousarray(im[...])  # rgb to bgr
    im = resize(cvtColor(im,COLOR_BGR2RGB),(im.shape[1]//3,im.shape[0]//3))
    return im

## Transform methods
### Transforming the first page to QR-png
def transform_pdf_to_png(pdf):
    pix = fitz.Pixmap(pdf, pdf.get_page_images(0)[0][0])  
    im = pix2np(pix)
    del(pix)
    return im

### Using opencv transformations to make QR-code more readable for system    
def transform_png(image):
    #Kernels
    kernel = np.array([[0, 0, 0],
                       [0, 1, 0],
                       [0, 0, 0]])
    filter_kernel = np.array([[0, -2, 0],
                              [-2, 12, -2],
                              [0, -2, 0]])
    sharpening_kernel = np.array([[-1, -1, -1],
                                  [-1, 30, -1],
                                  [-1, -1, -1]])
    cross_kernel= getStructuringElement(MORPH_CROSS,(5,5))
    rect_kernel =getStructuringElement(MORPH_RECT, (2,2))

    #Transformations
    image = filter2D(src=cvtColor(image, COLOR_BGR2HSV), ddepth=-1, kernel=kernel)
    thresh = threshold(image,200,255,THRESH_BINARY)[1]
    thresh = threshold(cvtColor(thresh, COLOR_HSV2RGB), 200, 255, THRESH_BINARY)[1]
    cmorphed_image = morphologyEx(cvtColor(thresh, COLOR_RGB2GRAY), MORPH_CLOSE, cross_kernel)
    
    filtered_image = filter2D(src=cmorphed_image, ddepth=-1, kernel=filter_kernel)
    omorphed_image = morphologyEx(cvtColor(cvtColor(filtered_image, COLOR_RGB2BGR), COLOR_BGR2GRAY), MORPH_OPEN, rect_kernel, iterations=4) 
    final_morphed_image = morphologyEx(morphologyEx(omorphed_image, MORPH_CLOSE, rect_kernel, iterations=4) , MORPH_OPEN, rect_kernel, iterations=4) 
    final_thresholded_image = threshold(final_morphed_image, 192, 255, THRESH_BINARY)[1]
    final_image = cvtColor(filter2D(src=final_thresholded_image, ddepth=5, kernel=sharpening_kernel), COLOR_GRAY2RGB)
    del image, thresh, filtered_image, omorphed_image, final_thresholded_image
    return final_image

## Remove first page
def remove_first_page(file):
    if file.pageCount > 1:
        pages = [p for p in range(file.page_count) if p>0]
        file.select(pages) 
    return file

## Main method (called by API main.py file)
def transform_file(file):
    try:
        pdf = fitz.open(f'{DATA_DIRECTORY}/{file}.pdf')
        image = transform_pdf_to_png(pdf)
        clean_image = transform_png(image)
        pdf_page = remove_first_page(pdf)
        pdf_page.saveIncr()
        del pdf,image
        return clean_image
    except fitz.FileDataError:
        raise fitz.FileDataError
    except FileNotFoundError:
        raise FileNotFoundError
            