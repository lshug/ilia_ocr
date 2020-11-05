import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras

LABEL_CHARS = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "?",
    "ა",
    "ბ",
    "გ",
    "დ",
    "ე",
    "ვ",
    "ზ",
    "თ",
    "ი",
    "კ",
    "ლ",
    "მ",
    "ნ",
    "ო",
    "პ",
    "ჟ",
    "რ",
    "ს",
    "ტ",
    "უ",
    "ფ",
    "ქ",
    "ღ",
    "ყ",
    "შ",
    "ჩ",
    "ც",
    "ძ",
    "წ",
    "ჭ",
    "ხ",
    "ჯ",
    "ჰ",
]
LABEL_ENCODINGS = dict(enumerate(LABEL_CHARS))
if not os.path.isfile(f"{os.path.dirname(__file__)}/model.h5"):
    keras.applications.ResNet152V2(include_top=True, weights=None, input_shape=(32,32,1), classes=len(LABEL_CHARS)).save(f"{os.path.dirname(__file__)}/model.h5")
model = keras.models.load_model(f"{os.path.dirname(__file__)}/model.h5")

def infer(img):
    img = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (32, 32)).reshape((32, 32, 1))[None]
    prediction = model.predict(img)
    label = LABEL_ENCODINGS[np.argmax(prediction[0])]
    return label
