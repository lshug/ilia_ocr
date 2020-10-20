import os
import random
from tqdm import tqdm
os.chdir('chars')
a = os.listdir()
b = [x+'.tmp' for x in a]
c = a[:]
random.shuffle(c)
for f,ft in tqdm(zip(a,b)):
    os.rename(f,ft)
for ft,fsh in tqdm(zip(b,c)):
    os.rename(ft,fsh)
