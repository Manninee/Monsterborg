import threading
import numpy as np
import time
import socket
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'  # Suppress tensorflow start messages

# TensorFlow 2.1
import tensorflow as tf
from tensorflow import convert_to_tensor
from tensorflow.python.saved_model import tag_constants, signature_constants
from tensorflow.python.framework import convert_to_constants


class OutputThread(threading.Thread):
    def __init__(self, port, ip, model, imageQueue, syncEvent):
        threading.Thread.__init__(self)
        self.end = False
        self.ip = ip
        self.port = port
        self.queue = imageQueue
        self.event = syncEvent

        self.enableControl = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Turn off power saving mode to make model loading faster
        print("Loading model")
        saved_model = tf.saved_model.load("./models/" + model, tags=[tag_constants.SERVING])
        graph_func = saved_model.signatures[signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
        self.graph_func = convert_to_constants.convert_variables_to_constants_v2(graph_func)
        print("Model loaded")

    def run(self):
        while not self.end:
            self.event.wait()

            # Get the received image from queue
            image = np.empty(shape=(0, 0))
            while not self.queue.empty():
                image = np.array(self.queue.get())

            command = ";"

            if image.shape == (360, 480, 3) and self.enableControl:
                start = time.time()
                image = image[170:, :]
                image = image.reshape(1, image.shape[0], image.shape[1], 3)
                image = image.astype('float32') / 255

                image = convert_to_tensor(image, dtype=np.float32)
                pred = self.graph_func(image)[0].numpy()

                e = np.argmax(pred)

                # Print neural network compute time
                print(time.time() - start)

                if e == 0:
                    command = "w,d;"
                elif e == 1:
                    command = "w,a;"
                elif e == 2:
                    command = "w;"

            # print(command)
            self.sendString(command)

            self.event.clear()

        print("Output ended")

    def sendString(self, string):
        try:
            self.socket.sendto(bytes(string, 'utf-8'), (self.ip, self.port))
        except:
            print("Could not send")

    def toggleControl(self):
        self.enableControl = not self.enableControl

    def sendEnd(self):
        self.sendString("end;")

    def stop(self):
        self.sendEnd()
        self.end = True
