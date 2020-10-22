from PIL import Image, ImageFilter
import numpy as np

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
    
pic = open_and_gray(r'chars\96.png')
pic = erode(pic, 3)
#pic = dilate(pic)
print(pic.shape)
Image.fromarray(np.uint8(pic)).save('test.png')
