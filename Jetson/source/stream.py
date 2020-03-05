import threading
import socket
import struct
from PIL import Image
import io
from time import sleep


class StreamThread(threading.Thread):
    def __init__(self, port, ip, q, sync):
        threading.Thread.__init__(self)
        self.end = False
        self.port = port
        self.address = ip
        self.queue = q
        self.sync = sync

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        self.socket.settimeout(2)
        print("Server listening")

    def run(self):
        while not self.end:
            try:
                self.socket.connect((self.address, self.port))
                connection = self.socket.makefile('rb')
                print("Connection made")
                while not self.end:
                    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
                    image_stream = io.BytesIO()
                    image_stream.write(connection.read(image_len))
                    image_stream.seek(0)

                    self.queue.put(Image.open(image_stream))
                    self.sync.set()

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
