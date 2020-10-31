from PIL import Image, ImageFilter
import numpy as np
from tesserocr import PyTessBaseAPI, RIL, PSM
from matplotlib import pyplot as plt
import cv2



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
    
    
api = PyTessBaseAPI(psm=PSM.SINGLE_WORD, path = r'C:\Program Files\Tesseract-OCR\tessdata')
api.Init(path = r'C:\Program Files\Tesseract-OCR\tessdata')


def resegment(img): #img needs to be a PIL image
   
    plt.imshow(img)
    
    
       
    with PyTessBaseAPI(psm=13, path = r'C:\Program Files\Tesseract-OCR\tessdata') as api:
        #api.Init(path = r'C:\Program Files\Tesseract-OCR\tessdata')
        print(api.GetPageSegMode())
        boxes = []
        api.SetImage(img)
        print("\nUPDATED!!!!\n")
        img_iter = api.AnalyseLayout()
        assert img_iter is not None
        boxes.append(img_iter.BoundingBox(RIL.SYMBOL))     
        while img_iter.Next(RIL.SYMBOL):
            
            boxes.append(img_iter.BoundingBox(RIL.SYMBOL))            
           
            
    plt.show() 
    
    return boxes

def extract_segments(img, ril=RIL.SYMBOL):
    cv_img = np.array(img.convert('RGB'))[:,:,::-1].copy()
    boxes = []
    with PyTessBaseAPI(psm=7, path = r'C:\Program Files\Tesseract-OCR\tessdata') as api:
        
        api.SetImage(img)
        img_iter = api.AnalyseLayout()
        boxes.append(img_iter.BoundingBox(ril))
        while img_iter.Next(ril):            
            boxes.append(img_iter.BoundingBox(ril))
            
        result = [Image.fromarray(cv_img[y:y+h, x:x+w]) for x,y,w,h in boxes]
        
    for box in result:
        plt.imshow(box)
        plt.show()
   
    return result


def refine_boxes(img, boxes):
    good_boxes, bad_boxes = filter_boxes(boxes)
    print(len(good_boxes))
    print(len(bad_boxes))
    

def filter_boxes(boxes):
    good_boxes = []
    to_be_refined = []
    for box in boxes:
        x, y, w, h = box
        ratio = w / h
        if ratio > 2: 
            to_be_refined.append(box)
        else:
            good_boxes.append(box)
    return good_boxes, to_be_refined



#pic = Image.open(r'1.png')
#boxes = resegment(pic)
pic = Image.open(r'41.png')
#boxes = resegment(pic)
extract_segments(pic)
#print(boxes)
#refine_boxes(pic, boxes)

#pic = erode(pic)

#Image.fromarray(np.uint8(pic)).save('test.png')
















