import os
import sys
import json
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras

LABEL_CHARS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?', 'ა', 'ბ', 'გ', 'დ', 'ე', 'ვ', 'ზ', 'თ', 'ი', 'კ', 'ლ', 'მ', 'ნ', 'ო', 'პ', 'ჟ', 'რ', 'ს', 'ტ', 'უ', 'ფ', 'ქ', 'ღ', 'ყ', 'შ', 'ჩ', 'ც', 'ძ', 'წ', 'ჭ', 'ხ', 'ჯ', 'ჰ']
LABEL_ENCODINGS = {y:x for x,y in enumerate(LABEL_CHARS)}
TRAIN_TEST_SPLIT = 0.8
LR = 0.0001
PATIENCE = 5

assert len(sys.argv)==2
label_dir = sys.argv[1]
assert os.path.isdir(label_dir)
assert os.path.isfile(label_dir+'/labels.txt')

train_path = os.getcwd()
os.chdir(label_dir)
label_dict = json.loads(open('labels.txt','r',encoding='utf8').read())

X = []
y = []

for char_f, label in label_dict.items():
    if (l := LABEL_ENCODINGS.get(label,None)) is None:
        continue
    y.append(l)
    im = cv2.resize(cv2.cvtColor(cv2.imread(char_f), cv2.COLOR_BGR2GRAY), (32,32)).reshape((32,32,1))
    X.append(im)

X = np.array(X) / 255.0
y = keras.utils.to_categorical(np.array(y), len(LABEL_CHARS))

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=TRAIN_TEST_SPLIT)

os.chdir(train_path)

optimizer = keras.optimizers.Adam(lr=LR)
callbacks = [tf.keras.callbacks.EarlyStopping(patience=PATIENCE), keras.callbacks.ModelCheckpoint(filepath='weights.h5',)]


model = keras.applications.ResNet152V2(include_top=True, weights=None, input_shape=(32,32,1), classes=len(LABEL_CHARS))

try:
    keras.models.load_model('./weights.h5')
except:
    pass

model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test,y_test), callbacks=callbacks)
model.save('trained.h5')
