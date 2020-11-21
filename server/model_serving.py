import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras

physical_devices = tf.config.list_physical_devices('GPU')
for device in physical_devices:
    try:
        tf.config.experimental.set_memory_growth(device, True)
    except:
        pass

LABEL_CHARS = list('0123456789?აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ')

LABEL_ENCODINGS = dict(enumerate(LABEL_CHARS))

if os.path.isfile(f"{os.path.dirname(__file__)}/model.h5"):
    model = keras.models.load_model(f"{os.path.dirname(__file__)}/model.h5")
else:
    model = keras.applications.ResNet152V2(include_top=True, weights=None, input_shape=(32,32,1), classes=len(LABEL_CHARS))
    model.predict(np.random.random_sample((1,32,32,1))) # ensure weight initialization

def predict(img):
    img = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (32, 32)).reshape((32, 32, 1))[None]
    prediction = model.predict(img)
    label = LABEL_ENCODINGS[np.argmax(prediction[0])]
    return label
