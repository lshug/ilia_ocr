from PIL import Image, ImageFilter
import numpy as np
from scipy.ndimage import maximum_filter
from tesserocr import PyTessBaseAPI, RIL


def segment(img, psm=7, ril=RIL.SYMBOL):
    with PyTessBaseAPI(psm=psm) as api:
        boxes = []
        api.SetImage(img)
        img_iter = api.AnalyseLayout()
        if img_iter is None:
            return boxes
        has_next = True
        while has_next:
            box = img_iter.BoundingBox(ril)
            if box is not None:
                boxes.append(box)
            has_next = img_iter.Next(ril)
    return boxes


def erode(im, size=3):
    im = Image.fromarray(im)
    im = im.filter(ImageFilter.MaxFilter(size))
    return im


def refine_boxes(img, boxes):
    good_boxes, bad_boxes = filter_boxes(boxes)
    img_np = np.asarray(img)
    for x, y, xw, yh in bad_boxes:
        im_temp = img_np[y:yh, x:xw]
        im_temp = erode(im_temp)
        new_boxes = segment(im_temp)
        new_boxes_rebased = [(box[0] + x, box[1] + y, box[2] + x, box[3] + y) for box in new_boxes]
        good_boxes = good_boxes + new_boxes_rebased
    return good_boxes


def refine(img, page_json, page):
    len_paragraphs = len(page_json)
    for i, p in enumerate(page_json):
        page.progress = (
            f"Resegmenting paragraph {i}/{len_paragraphs}",
            i / len_paragraphs,
        )
        for w in p["words"]:
            all_chars = w["chars"]
            empty_chars = [b for b in all_chars if b["label"] == ""]
            punctuation_chars = empty_chars = [b for b in all_chars if b["label"] != ""]
            boxes = [c["box"] for c in empty_chars]
            boxes = refine_boxes(img, boxes)
            refined_chars = [{"box": box, "label": ""} for box in boxes]
            w["chars"] = punctuation_chars + refined_chars
    page.progress = (f"Done resegmenting paragraphs", 1.0)
    return page_json


def filter_boxes(boxes):
    good_boxes = []
    bad_boxes = []
    for box in boxes:
        x, y, xw, yh = box
        w, h = x - xw, y - yh
        if h == 0:
            continue
        ratio = w / h
        if ratio > 2:
            bad_boxes.append(box)
        else:
            good_boxes.append(box)
    return good_boxes, bad_boxes
