import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'  # Suppress tensorflow start messages

import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
import matplotlib.pyplot as plt
import numpy as np


def defineMoldel(input_size):
    # Filters less -> more [32-128] -> [256-1024]
    # Filter size bigger -> smaller 7x7 -> 5x5 -> 3x3
    # Pooling 2x2 maybe
    # Dropout max 0.5
    model = models.Sequential()
    model.add(layers.Conv2D(32, 7, padding='same', activation='relu', input_shape=input_size))
    model.add(layers.MaxPooling2D(2))

    model.add(layers.Conv2D(32, 5, padding='same', activation='relu'))
    model.add(layers.MaxPooling2D(2))

    model.add(layers.Conv2D(64, 5, padding='same', activation='relu'))
    model.add(layers.MaxPooling2D(2))

    model.add(layers.Conv2D(64, 3, padding='same', activation='relu'))
    model.add(layers.MaxPooling2D(2))

    model.add(layers.Conv2D(128, 3, padding='same', activation='relu'))
    model.add(layers.MaxPooling2D(2))

    model.add(layers.Flatten())
    model.add(layers.Dense(150, activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(75, activation='relu'))
    model.add(layers.Dropout(0.3))
    model.add(layers.Dense(25, activation='relu'))
    model.add(layers.Dense(3, activation='softmax'))

    model.summary()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    return model


def main():
    # frames 480x190
    model = defineMoldel((190, 480, 3))

    images = np.memmap("X:\images.dat", dtype='float32', mode='r', shape=(58745, 190, 480, 3))
    labels = np.memmap("X:\commands.dat", dtype='float32', mode='r', shape=(58745, 3))

    history = model.fit(images, labels, epochs=5, validation_split=0.15, verbose=2, batch_size=128)

    tf.saved_model.save(model, "Model")
    model.save("model.h5")

    plt.figure()
    plt.plot(history.history['accuracy'], label='accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.ylim([0.4, 1])
    plt.legend(loc='lower right')
    plt.show()


main()
