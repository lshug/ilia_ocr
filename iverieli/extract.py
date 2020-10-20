from PIL import Image
from tesserocr import PyTessBaseAPI, RIL
import numpy as np
import cv2

api = PyTessBaseAPI()
api.Init()

def extract_segments(img, psm=1):
    cv_img = np.array(img.convert('RGB'))[:,:,::-1].copy()
    boxes = []
    api.SetImage(p)
    img_iter = api.AnalyseLayout()
    while img_iter.Next(psm):
        boxes.append(img_iter.BoundingBox(psm))
    return [Image.fromarray(cv_img[y:y+h, x:x+w]) for x,y,w,h in boxes]

def extract_chars(img, psm=1):
    api.SetImage(img)
    return [b[0] for b in api.GetComponentImages(RIL.SYMBOL, True)]
        
    
if __name__ == '__main__':
    import os
    from tqdm import tqdm
    os.chdir('dataset')
    dirs = os.listdir()
    for d in tqdm(dirs):
        os.chdir(d)
        pages = [x for x in os.listdir() if x!='chars']
        try:
            os.mkdir('chars')
        except:
            pass
        for p in pages:
            img = Image.open(p)
            chars = extract_chars(img)
            for i,im in enumerate(chars):
                im.save(f'chars/{i}.png','PNG')
        os.chdir('..')
