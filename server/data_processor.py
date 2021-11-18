import os
import io
import requests
import asyncio
from PIL import Image
from bs4 import BeautifulSoup
import numpy as np
from .server_utils import celery_app
from celery.signals import worker_process_init
from celery.utils.log import get_task_logger
from .utils import refine
from .models import retrieve_page, async_retrieve_raw_file, postgresql_retrieve_raw_file_contents
from .settings import settings


import locale
locale.setlocale(locale.LC_ALL, 'C')
from tesserocr import PyTessBaseAPI, RIL

logger = get_task_logger(__name__)

punctuations = list("'" + '.,"`_-/\\?!–’—”„%()')
LABEL_CHARS = list('0123456789?აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ')
LABEL_ENCODINGS = dict(enumerate(LABEL_CHARS))

def process_hocr(hocr, img, page):
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
                c_label = c_label if c_label in punctuations or c_label in LABEL_CHARS else ''
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

def process_image(img, page, refine_boxes):
    try:
        page.progress = ('Analysing layout', 0.0)
        with PyTessBaseAPI(lang='ge', psm=3) as api:
            api.SetVariable("hocr_char_boxes", "true")
            api.SetImage(img)
            api.Recognize()
            hocr = api.GetHOCRText(0)
        page.progress = ('Analysing layout', 1.0)
        page_json = process_hocr(hocr, img, page)
        if refine_boxes:
            page_json = refine(img, page_json, page)
        page_json_to_text(page_json, page)
        return page_json
    except:
        page.progress = (f"Error processing page: {e}", -1)
        return {}


@celery_app.task(name='process_images')
def process_images(file_ids, pages, refine_boxes, callback_url):
    db_mode = 'sqlite' if 'sqlite' in settings.database_url else 'postgresql'
    pages = [retrieve_page(p) for p in pages]
    page_jsons = []
    for idx, (page, file_id) in enumerate(zip(pages, file_ids)):
        try:
            if db_mode == 'sqlite':
                record = asyncio.run(async_retrieve_raw_file(file_id))
                try:
                    img_bytes = record['contents']
                except:
                    img_bytes = record.contents
            else:
                img_bytes = postgresql_retrieve_raw_file_contents(file_id)
        except Exception as ex:
            logger.error(f'{db_mode}: {ex}')
            page.progress = (f"file with id {file_id} not found.", -1)
            continue
        try:
            img = Image.open(io.BytesIO(img_bytes))
        except Exception as ex:
            page.progress = (f'Unable to open image with id {file_id}: {ex}')
            continue
        page_jsons.append(process_image(img, page, refine_boxes))
        if callback_url != '':
            try:
                requests.get(callback_url, page=idx + 1, total=len(pages))
            except:
                pass
    
    return page_jsons
    
