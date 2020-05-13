import threading
import socket


class UdpThread(threading.Thread):
    def __init__(self, ip, port, queue, event, sync):
        threading.Thread.__init__(self)
        self.end = False
        self.ip = ip
        self.port = port
        self.queue = queue
        self.event = event
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sync = sync
        self.interval = 0.2

    def run(self):
        while not self.end:
            self.event.set()
            self.sync.wait(self.interval)

            if not self.queue.empty():
                command = self.queue.get()
            else:
                command = ";"

            self.sendString(command)

            self.sync.clear()

        self.sendString("end;")
        print("UDP ended")

    def sendString(self, string):
        try:
            self.socket.sendto(bytes(string, 'utf-8'), (self.ip, self.port))
        except:
            print("Could not send")

    def stop(self):
        self.end = True
