import threading
import socket
import io
import picamera
import struct
from time import sleep


class SplitFrames(object):
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)


class StreamThread(threading.Thread):
    def __init__(self, port, end):
        threading.Thread.__init__(self)
        self.port = port
        self.end = end

        self.camera = picamera.PiCamera(resolution=(480, 360), framerate=30)
        self.camera.rotation = 180

        self.socket = socket.socket()

        # Restart loop to wait for socket to be free
        while True:
            try:
                self.socket.bind(('0.0.0.0', port))
                break
            except socket.error as e:
                if str(e).startswith("[Errno 98]"):
                    sleep(3)
                    print("Trying to bind address")
                else:
                    raise Exception(e)

        self.socket.listen(0)
        self.socket.setblocking(False)
        self.socket.settimeout(2)
        print("Server listening")

    def run(self):
        while not self.end.is_set():
            try:
                connection = self.socket.accept()[0].makefile('rb')
                print("Connection made")
                output = SplitFrames(connection)
                self.camera.start_recording(output, format='mjpeg')
                while not self.end.is_set():
                    self.camera.wait_recording(0)

                connection.close()
                print("Connection closed")
            except socket.timeout:
                # print("No connection")
                pass
            except socket.error:
                print("Connection closed error")

        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print("Stream ended")
