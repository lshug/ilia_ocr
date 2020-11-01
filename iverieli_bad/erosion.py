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
   
    
       
    with PyTessBaseAPI(psm=6, path = r'C:\Program Files\Tesseract-OCR\tessdata') as api:
        #api.Init(path = r'C:\Program Files\Tesseract-OCR\tessdata')
       
        boxes = []
        api.SetImage(img)
        img_iter = api.AnalyseLayout()
        assert img_iter is not None
        boxes.append(img_iter.BoundingBox(RIL.SYMBOL))     
        while img_iter.Next(RIL.SYMBOL):
            
            boxes.append(img_iter.BoundingBox(RIL.SYMBOL))            
     
    return boxes



def refine_boxes(img, boxes):
    good_boxes, bad_boxes = filter_boxes(boxes)
    
    for bad_box in bad_boxes:
        x, y, w, h = bad_box
        im_temp = np.asarray(img)[y:y+h, x:x+w]
        
        # SEGMENTATION LOGIC START
        im_temp = erode(im_temp)
        # SEGMENTATION LOGIC END
        
        plt.imshow(im_temp)
        plt.show()
        
        im = Image.fromarray(im_temp)
        new_boxes = resegment(im.convert('RGB'))
        for i in range(len(new_boxes)):
            im_t = np.asarray(im_temp)[new_boxes[i][1]:new_boxes[i][1]+new_boxes[i][3], new_boxes[i][0]:new_boxes[i][0]+new_boxes[i][2]]
            plt.imshow(im_t)
            plt.show()
            new_boxes[i] = (new_boxes[i][0] + x, new_boxes[i][1] + y, new_boxes[i][2] + w, new_boxes[i][3] + h)
            
            
            
        print(len(new_boxes))
        np.append(good_boxes, new_boxes)
        
   
    
    return good_boxes
    
        
    

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




pic = Image.open(r'41.png')
boxes = resegment(pic)
print(boxes)
refine_boxes(pic, boxes)

#pic = erode(pic)

#Image.fromarray(np.uint8(pic)).save('test.png')
















