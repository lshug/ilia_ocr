import os
from tqdm import tqdm
from pdf2image import convert_from_path
from extract import extract_chars
import fitz
import random
from PIL import Image

try:
    os.mkdir('dataset')
    os.mkdir('chars')
except:
    pass


files = [x for x in os.listdir('.') if '.pdf' in x]
random.shuffle(files)

if extract_no := os.getenv('EXTRACT_NO',None) is not None:
    files = files[:extract_no]
    
error = 0
for f in tqdm(files):
    try:
        "Extract pdf text, append to iverieli_text_corpus.txt"
        with fitz.open(f) as doc:
            text = ''
            for page in doc:
                text += page.getText()
        open('iverieli_text_corpus.txt','a+', encoding='utf8').write(text)
    except:
        pass
    try:
        new_dir = 'dataset/' + f.split('.pdf')[0]
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)
            convert_from_path(f, fmt='png', output_folder=new_dir)
            os.chdir(new_dir)
            pages = [x for x in os.listdir() if 'png' in x and x != 'chars']
            try:
                os.mkdir('chars')
            except:
                pass
            for p in pages:
                img = Image.open(p)
                chars = extract_chars(img)
                for i,im in tqdm(enumerate(chars)):
                    im.save(f'chars/{i}.png','PNG')
            os.chdir('../..')
    except Exception as ex:
        error+=1
print(f'Failed converting {error}/{len(files)} pdfs')
    
    
