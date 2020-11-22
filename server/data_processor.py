import io
import asyncio
import numpy as np
from PIL import Image
from bs4 import BeautifulSoup
from .server_utils import celery_app
from .model_serving import predict
from .utils import refine
from .models import retrieve_page, retrieve_raw_file
from .settings import settings

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

def process_image(img, page, refine_boxes, latin_mode):
    try:
        page.progress = ('Analysing layout', 0.0)
        with PyTessBaseAPI(psm=3) as api:
            api.SetVariable("hocr_char_boxes", "true")
            api.SetImage(img)
            api.Recognize()
            hocr = api.GetHOCRText(0)
        page.progress = ('Analysing layout', 1.0)
        page_json = process_hocr(hocr, img, page, latin_mode)
        if refine_boxes:
            page_json = refine(img, page_json, page)
        page_json_to_text(page_json, page)
        return page_json
    except:
        page.progress = (f"Error processing page: {e}", -1)
        return {}


@celery_app.task(name='process_images')
def process_images(file_ids, pages, refine_boxes, latin_mode):
    pages = [retrieve_page(p) for p in pages]
    page_jsons = []
    for page, file_id in zip(pages, file_ids):
        img_bytes = asyncio.run(retrieve_raw_file(file_id)).contents
        img = Image.open(io.BytesIO(img_bytes))
        page_jsons.append(process_image(img, page, refine_boxes, latin_mode))
    return page_jsons
    
