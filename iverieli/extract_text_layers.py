from tqdm import tqdm
import random
import fitz

files = [x for x in os.listdir('.') if '.pdf' in x]
random.shuffle(files) 

for f in tqdm(files):
    try:
        "Extract pdf text, append to iverieli_text_corpus.txt"
        with fitz.open(f) as doc:
            text = ''
            for page in doc:
                text += page.getText()
        text += '\n\n\n\n'
        open('iverieli_text_corpus.txt','a+', encoding='utf8').write(text)
    except:
        pass
