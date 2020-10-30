# Model training

Code here should load a labelled char folder, load the chars and labels into numpy arrays, train the model, and export a keras model h5. Char path should be provided as a command line argument. 

Example: `python3 train.py "/home/user/labeled_chars/"`

#### Input:
```(28,28), float32```

####  Classes:
```['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?', 'ა', 'ბ', 'გ', 'დ', 'ე', 'ვ', 'ზ', 'თ', 'ი', 'კ', 'ლ', 'მ', 'ნ', 'ო', 'პ', 'ჟ', 'რ', 'ს', 'ტ', 'უ', 'ფ', 'ქ', 'ღ', 'ყ', 'შ', 'ჩ', 'ც', 'ძ', 'წ', 'ჭ', 'ხ', 'ჯ', 'ჰ']
```

#### Preprocessing
All samples are divided by 255.0.

#### Model, hyperparameters and schedule
 * InceptionResNetV2 with `(28,28) float32` input and 44 class output.
 * 0.8 train-test split
 * Categorical cross-entropy loss
 * Adam with `lr=0.0001`
 * `epochs=20`, `batch_size=32`
 * Early stopping monitoring validation loss with `patience=5`
 * Restore best weights after stop
