from threading import Event
from queue import Queue

from source.stream import StreamThread
from source.udp import UdpThread
from source.gui import App
from source.saver import SavingThread
from source.inputs import InputsThread


def main():
    streamQueue = Queue()
    udpQueue = Queue()
    commandQueue = Queue()
    imageQueue = Queue()
    udpEvent = Event()
    saveEvent = Event()
    syncEvent = Event()

    ip = "192.168.1.1"

    inputs = InputsThread(udpQueue, udpEvent, saveEvent, commandQueue)
    saver = SavingThread(saveEvent, imageQueue, commandQueue)
    stream = StreamThread(5001, ip, streamQueue, saveEvent, syncEvent, imageQueue)
    app = App("MosterBorg Gui", streamQueue, inputs, saveEvent)
    udp = UdpThread(ip, 5000, udpQueue, udpEvent, syncEvent)

    udp.start()
    inputs.start()
    stream.start()
    saver.start()

    app.run()

    print("Main exiting")

    saver.stop()
    inputs.stop()
    stream.stop()
    udp.stop()

    udpEvent.set()
    saveEvent.set()


main()
