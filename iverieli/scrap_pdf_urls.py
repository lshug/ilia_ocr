import requests
import urllib.request
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import random

browser_url = 'http://dspace.nplg.gov.ge/handle/1234/94/browse?type=dateissued&sort_by=2&order=ASC&rpp=100&etal=-1&null=&offset='
handles = []
for i in tqdm(range(814)):
    try:
        r = requests.get(browser_url + str(i*100))
        soup = BeautifulSoup(r.text)
        rows = soup.body.find('table', attrs={'class':'table'}).find_all('tr')[1:]
        for r in rows:
            handle = r.find_all('td')[2].find('a',href=True)['href']
            handles.append(handle)
    except:
        pass

files = []
for h in tqdm(handles):
    try:
        r = requests.get('http://dspace.nplg.gov.ge/'+h)
        soup = BeautifulSoup(r.text)
        rows = soup.body.find('table', attrs={'class':'table panel-body'}).find_all('tr')[1:]
        for r in rows:
            f = r.find('a',href=True)['href']
            files.append(f)
    except:
        pass

files = ['http://dspace.nplg.gov.ge'+f for f in files]


nongeo_strings = list('АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя') + ['Nedelia','Vedomosti','Listok','Figaro','Xleb','Bzyb','Borba','Vechernii','Volni','Golos','Rabochii','Gruzia','Zabava','Zakavkaz','Kavkaz','Kavkaski','kavkaz','Novoe','Novii','Pravda','Apsny','Messenger','Times','41_Grad','Journal','Kaukasische','Georgiana','Georgie','Observer']
def georgian(s):
    return all([n not in s for n in nongeo_strings])

files = list(filter(georgian, files))
open('file_urls.txt','w',encoding='utf8').writelines([f+'\n' for f in files])
random.shuffle(files)
open('file_urls_shuffled.txt','w',encoding='utf8').writelines([f+'\n' for f in files])
open('file_urls_shuffled_10k.txt','w',encoding='utf8').writelines([f+'\n' for f in files[:10000]])


for f in tqdm(files[0:10000]):
    urllib.request.urlretrieve(f, f.split('/')[-1])
