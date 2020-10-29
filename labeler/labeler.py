import os
import tkinter as tk
import tkinter.filedialog
import json
from PIL import ImageTk, Image


root = tk.Tk()
root.title("ilia_ocr labeler")
root.geometry('400x400+600+600')

root.withdraw()
char_directory = tk.filedialog.askdirectory(title='Character directory', parent=root)
os.chdir(char_directory)
files = [x for x in os.listdir() if 'png' in x]
files.sort()

root.deiconify()
root.lift()
root.focus_force()

def char_entry(char):
    label_dir[files[current_image]]=char
    right()

def left():
    global current_image
    current_image = (current_image - 1) % len(files)
    update()
    
def right():
    global current_image
    current_image = (current_image + 1) % len(files)
    update()


def bad():
    label_dir[files[current_image]]='bad'
    right()

def update():
    img = ImageTk.PhotoImage(Image.open(char_directory+'/'+files[current_image]).resize((400,300)))
    imgpanel.configure(image=img)
    imgpanel.image = img
    current_text.set(label_dir.get(files[current_image],''))



def key(event):
    if event.keysym=='space':
        bad()
    elif len(event.char)==1:
        char_entry(event.char)
        current_text.set('')
    elif event.keysym=='Left':
        current_text.set('')
        left()
    elif event.keysym=='Right':
        current_text.set('')
        right()

try:
    label_dir = json.loads((open('labels.txt','r',encoding='utf8').read()))
    for k in label_dir.keys():
        files.remove(k)
except Exception as e:
    label_dir = {}
    open("labels.txt","w+",encoding='utf8')

current_image = 0
img = ImageTk.PhotoImage(Image.open(char_directory+'/'+files[current_image]).resize((400,300)))
imgpanel = tk.Label(root, image=img)
imgpanel.pack(side="top", fill="both", expand="yes")

current_text = tk.StringVar()
current_text.set(label_dir.get(files[current_image],''))
entry = tk.Entry(root, textvariable=current_text)
entry.bind('<Key>', key)
entry.focus_force()
entry.pack(side='bottom', fill='both', expand='yes')


root.mainloop()

open("labels.txt","w",encoding='utf8').write(json.dumps(label_dir,ensure_ascii=False))
