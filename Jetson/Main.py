from threading import Event
from queue import Queue
# from time import sleep

from source.stream import StreamThread
from source.output import OutputThread


def main():
    streamQueue = Queue()
    streamEvent = Event()

    ip = "192.1.1.251"

    stream = StreamThread(5001, ip, streamQueue, streamEvent)
    output = OutputThread(5000, ip, 'Model_1.6m_RGB_TRT', streamQueue, streamEvent)

    output.start()
    stream.start()

    print("Threads started")
    try:
        while True:
            e = input().lower()

            if e == "q":
                stream.stop()
                output.sendEnd()

            elif e == "startstream" or e == "ss":
                stream = StreamThread(5001, ip, streamQueue, streamEvent)
                stream.start()

            elif e == "move" or e == "m":
                output.toggleControl()

            elif e == "quit":
                break

    except KeyboardInterrupt:
        pass

    print("Program ending")

    output.stop()
    stream.stop()
    streamEvent.set()

main()
