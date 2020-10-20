import os
from tqdm import tqdm
from pdf2image import convert_from_path

poppler_path = 'D:/iverieli/poppler'

files = [x for x in os.listdir('.') if '.pdf' in x]
error = 0
for f in tqdm(files):
    try:
        new_dir = 'dataset/'+f.split('.pdf')[0]
        if not os.path.isdir(new_dir):
            os.mkdir(new_dir)
            convert_from_path(f, fmt='png', output_folder=new_dir, poppler_path=poppler_path)
    except:
        error+=1
print(f'Failed converting {error}/{len(files)} pdfs')
    
    
