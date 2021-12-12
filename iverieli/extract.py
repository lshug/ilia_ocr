from PIL import Image
from tesserocr import PyTessBaseAPI, RIL
import numpy as np
import cv2

api = PyTessBaseAPI(psm=1)
api.Init()

def extract_segments(img, ril=RIL.SYMBOL):
    cv_img = np.array(img.convert('RGB'))[:,:,::-1].copy()
    boxes = []
    api.SetImage(img)
    img_iter = api.AnalyseLayout()
    while img_iter.Next(ril):
        boxes.append(img_iter.BoundingBox(ril))
    return [Image.fromarray(cv_img[y:y+h, x:x+w]) for x,y,w,h in boxes]

def extract_chars(img, psm=1):
    api.SetImage(img)
    return [b[0] for b in api.GetComponentImages(RIL.SYMBOL, True)]

def extract_lines(img, psm=1):
    api.SetImage(img)
    return [b[0] for b in api.GetComponentImages(RIL.TEXTLINE, True)]    
    
if __name__ == '__main__':
    import os
    from tqdm import tqdm
    os.chdir('dataset')
    dirs = os.listdir()
    for d in tqdm(dirs):
        os.chdir(d)
        pages = [x for x in os.listdir() if x != 'chars' and x != 'lines']
        try:
            os.mkdir('chars')
            os.mkdir('lines')
        except:
            pass
        for p in pages:
            img = Image.open(p)
            chars = extract_chars(img)
            lines = extract_lines(img)
            for col in [chars, lines]:
                for idx, im in enumerate(col):
                    im.save(f'chars/{idx}.png','PNG')            
        os.chdir('..')
