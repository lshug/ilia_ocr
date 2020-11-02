import re
import os
from tqdm import tqdm
from PIL import Image
from tesserocr import PyTessBaseAPI, RIL
from pdf2image import convert_from_path
from utils import segment, refine_boxes
from bs4 import BeautifulSoup

punctuations = list("'" + '.,"`_-/\\?!–’—”„%()')

def process_hocr(hocr, img = None):
    pars_out = []
    soup = BeautifulSoup(hocr)
    paragraphs = soup.body.find_all('p', attrs={'class':'ocr_par'})
    for p in tqdm(paragraphs, 'Processing paragraphs'):
        p_box = tuple([int(x) for x in p.attrs['title'].split(';')[0].split(' ')[1:]])
        words_out = []
        words = p.find_all('span', attrs={'class':'ocrx_word'})
        for w in tqdm(words, 'Processing words'):
            w_box = tuple([int(x) for x in w.attrs['title'].split(';')[0].split(' ')[1:]])
            chars_out = []
            chars = w.find_all('span', attrs={'class':'ocrx_cinfo'})
            for c in tqdm(chars, 'Processsing characters'):
                c_box = tuple([int(x) for x in c.attrs['title'].split(';')[0].split(' ')[1:]])
                c_label = c.text
                c_label = c_label if c_label in punctuations else ''
                chars_out.append({'box':c_box, 'label':c_label})
            words_out.append({'box':p_box, 'chars':chars_out})
        pars_out.append({'box':p_box, 'words':words_out})
    return pars_out

def process_pdf(path):
    pdf_file = path + '/' + os.listdir(path)[0]
    convert_from_path(pdf_file, fmt='png', output_folder=path)
    return process_images(path)

def process_images(path):
    os.chdir(path)
    img_paths, page_jsons = [], []
    for img_path in tqdm([f for f in os.listdir() if '.png' in f], 'Processing images'):
        img = Image.open(img_path)
        with PyTessBaseAPI(psm=3) as api:
            api.SetVariable('hocr_char_boxes', 'true')
            api.SetImage(img)
            api.Recognize()
            hocr = api.GetHOCRText(0)
        page_json = process_hocr(hocr, img)
        img_paths.append(img_path)
        page_jsons.append(page_json)
    return img_paths, page_jsons

    
