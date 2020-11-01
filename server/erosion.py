from PIL import Image, ImageFilter
import numpy as np
from tesserocr import PyTessBaseAPI, RIL



def erode(im, size=3):
    im = Image.fromarray(im)
    im = im.filter(ImageFilter.MaxFilter(size))
    return im


def resegment(img, psm=7):
    with PyTessBaseAPI(psm=psm) as api:
        boxes = []
        api.SetImage(img)
        img_iter = api.AnalyseLayout()
        boxes.append(img_iter.BoundingBox(RIL.SYMBOL))
        while img_iter.Next(RIL.SYMBOL):
            boxes.append(img_iter.BoundingBox(RIL.SYMBOL))
    return boxes


def refine_boxes(img, boxes):
    good_boxes, bad_boxes = filter_boxes(boxes)
    img_np = np.asarray(img)
    for x, y, xw, yh in bad_boxes:
        im_temp = img_np[y : yh, x : xw]
        im_temp = erode(im_temp)
        new_boxes = resegment(im_temp)
        new_boxes_rebased = [(box[0]+x, box[1]+y, box[2]+x, box[3]+y) for box in new_boxes]
        good_boxes = good_boxes + new_boxes_rebased
    return good_boxes


def filter_boxes(boxes):
    good_boxes = []
    bad_boxes = []
    for box in boxes:
        x, y, xw, yh = box
        w,h = x - xw, y - yh
        ratio = w / h
        if ratio > 2:
            bad_boxes.append(box)
        else:
            good_boxes.append(box)
    return good_boxes, bad_boxes


