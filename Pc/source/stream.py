import threading
import socket
import struct
from PIL import Image
import io
from time import sleep
# import cv2
# import numpy

class StreamThread(threading.Thread):
    def __init__(self, port, ip, q, save, sync, saveImageQueue):
        threading.Thread.__init__(self)
        self.end = False
        self.socket = socket.socket()
        self.queue = q
        self.save = save
        self.sync = sync
        self.saveQueue = saveImageQueue
        self.port = port
        self.address = ip

        self.socket.setblocking(False)
        self.socket.settimeout(1)
        print("Server listening")

    def run(self):
        while not self.end:
            sleep(2)
            try:
                self.socket.connect((self.address, self.port))
                connection = self.socket.makefile('rb')
                print("Connection made")
                while not self.end:
                    self.sync.set()
                    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                    image_stream = io.BytesIO()
                    image_stream.write(connection.read(image_len))
                    image_stream.seek(0)

                    image = Image.open(image_stream)

                    if self.save.is_set():
                        self.saveQueue.put(image.copy())

                    self.queue.put(image)

                connection.close()
                print("Connection closed")
            except BlockingIOError:
                print("Already in progress")
                sleep(3)
            except socket.timeout:
                # print("No connection")
                pass
            except OSError:
                print("Could not find robot")
                sleep(3)
            except struct.error:
                print("Could not connect to camera")

        self.socket.close()
        print("Stream ended")

    def stop(self):
        self.end = True
