import json
import os

combined = {}
folders = [x for x in os.listdir() if '.py' not in x]
os.mkdir('combined')

for f in folders:
    d = json.loads(open(f+'/labels.txt','r',encoding='utf8').read())
    for k,v in d.items():
        combined[f+'_'+k] = v
    for im in [x for x in os.listdir(f) if '.png' in x]:
        os.rename(f+'/'+im, f'combined/{f}_'+im)

open("combined/labels.txt","w",encoding='utf8').write(json.dumps(combined,ensure_ascii=False))
