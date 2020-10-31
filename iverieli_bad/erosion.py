from PIL import Image, ImageFilter
import numpy as np
from tesserocr import PyTessBaseAPI, RIL

api = PyTessBaseAPI(psm=1, path = r'C:\Program Files\Tesseract-OCR\tessdata')
api.Init(path = r'C:\Program Files\Tesseract-OCR\tessdata')


def open_and_gray(filename):
        im = Image.open(filename)
        im_np = np.asarray(im)
        temp = np.ones(im_np.shape) * 255

        temp[im_np < 40] = 0
        
        return temp

def erode(im, size=3):
        tmp = np.copy(im)
        im = Image.fromarray(im)
        im = im.filter(ImageFilter.MaxFilter(size))
        im = np.asarray(im)
        return im

def dilate(im, size=3):
        tmp = np.copy(im)
        im = Image.fromarray(im)
        im = im.filter(ImageFilter.MinFilter(size))
        im = np.asarray(im)
        return im
    
    

def resegment(img): #img needs to be a PIL image
    boxes = []
    api.SetImage(img)
    img_iter = api.AnalyseLayout()
    print(img_iter is None)
    while img_iter.Next(RIL.SYMBOL):
        boxes.append(img_iter.BoundingBox(RIL.SYMBOL))
    return boxes



pic = Image.open(r'2.png')
    
print(resegment(pic))

#pic = erode(pic)

#Image.fromarray(np.uint8(pic)).save('test.png')
















