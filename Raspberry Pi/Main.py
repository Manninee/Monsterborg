from threading import Event
from source.stream import StreamThread
from source.motors import MotorSpeedControlThread
from source.udp import UdpThread


def main():
    endEvent = Event()

    stream = StreamThread(5001, endEvent)
    motors = MotorSpeedControlThread(endEvent)
    udp = UdpThread(5000, endEvent, motors)

    stream.start()
    udp.start()
    motors.start()


main()