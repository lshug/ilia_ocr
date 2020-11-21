import os
import numpy as np
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
from bs4 import BeautifulSoup
from .model_serving import predict
from .utils import refine
from .models import retrieve_page

import locale
locale.setlocale(locale.LC_ALL, 'C')
from tesserocr import PyTessBaseAPI, RIL


punctuations = list("'" + '.,"`_-/\\?!–’—”„%()')


def process_hocr(hocr, img, page, latin_mode):
    img_np = np.asarray(img)
    pars_out = []
    soup = BeautifulSoup(hocr, features="lxml")
    paragraphs = soup.body.find_all("p", attrs={"class": "ocr_par"})
    len_paragraphs = len(paragraphs)
    for i, p in enumerate(paragraphs):
        page.progress = (f"Processing paragraph {i}/{len_paragraphs}", i / len_paragraphs)
        p_box = tuple([int(x) for x in p.attrs["title"].split(";")[0].split(" ")[1:]])
        words_out = []
        words = p.find_all("span", attrs={"class": "ocrx_word"})
        for w in words:
            w_box = tuple([int(x) for x in w.attrs["title"].split(";")[0].split(" ")[1:]])
            chars_out = []
            chars = w.find_all("span", attrs={"class": "ocrx_cinfo"})
            for c in chars:
                c_box = tuple([int(x) for x in c.attrs["title"].split(";")[0].split(" ")[1:]])
                x, y, xw, yh = c_box
                c_label = c.text
                if not latin_mode:
                    c_label = c_label if c_label in punctuations else predict(img_np[y:yh, x:xw])  # Inference is made here
                chars_out.append({"box": c_box, "label": c_label})
            words_out.append({"box": p_box, "chars": chars_out})
        pars_out.append({"box": p_box, "words": words_out})
    page.progress = (f"Done processing paragraphs", 1.0)
    return pars_out


def page_json_to_text(page_json, page):
    len_paragraphs = len(page_json)
    text = ""
    for i, p in enumerate(page_json):
        page.progress = (f"Formatting paragraph text {i}/{len_paragraphs}", i / len_paragraphs)
        for w in p["words"]:
            for c in w["chars"]:
                text += c["label"]
            text += " "
        text += "\n"
    page.text = text
    page.progress = ("Ready", 1.0)


def convert_pdf(f, output_folder):
    convert_from_bytes(f, fmt="png", output_folder=output_folder, output_file='')

def process_image(img, page, refine_boxes, latin_mode):
    try:
        with PyTessBaseAPI(psm=3) as api:
            api.SetVariable("hocr_char_boxes", "true")
            api.SetImage(img)
            api.Recognize()
            hocr = api.GetHOCRText(0)
        page_json = process_hocr(hocr, img, page, latin_mode)
        if refine_boxes:
            page_json = refine(img, page_json, page)
        page_json_to_text(page_json, page)
        return page_json
    except:
        page.progress = (f"Error processing page: {e}", -1)
        return {}

def process_images(path, doc, refine_boxes, latin_mode):
    doc_pages = [retrieve_page(p) for p in doc.pages]
    page_jsons = []
    for i, img_path in enumerate([f for f in os.listdir(path) if ".pdf" not in f]):
        img = Image.open(f'{path}/{img_path}')
        page_jsons.append(process_image(img, doc_pages[i], refine_boxes, latin_mode))
    return page_jsons
    
