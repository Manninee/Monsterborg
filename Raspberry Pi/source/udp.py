import threading
import socket


class UdpThread(threading.Thread):
    def __init__(self, port, end, motors):
        threading.Thread.__init__(self)
        self.port = port
        self.end = end
        self.motors = motors

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", self.port))

    def run(self):
        while True:
            data, addr = self.socket.recvfrom(256)
            data = data.decode('utf-8')

            commands = data.split(";")
            keyboardCommands = commands[0].split(",")

            if "end" in keyboardCommands:
                self.end.set()
                break

            if len(commands[1]) != 0:
                self.controllerControls(commands[1].split(","))
            else:
                self.keyboardControls(keyboardCommands)

        print("udp end")

    def keyboardControls(self, commands):
        speed = 0
        direction = 0

        if "w" in commands:
            speed = speed + 0.7

        if "s" in commands:
            speed = speed - 0.7

        if "a" in commands:
            direction = direction - 1

        if "d" in commands:
            direction = direction + 1

        if "space" in commands:
            speed = speed * 2

        self.motors.setMotorTargetSpeed(speed, direction)

    def controllerControls(self, commands):
        axes = [round(float(i), 3) for i in commands[:4]]
        buttons = [int(i) for i in commands[4:]]

        speed = axes[1] * (-1)
        direction = axes[2] * (-1)

        if buttons[9] == 0:  # R2 button pressed
            speed /= 2

        self.motors.setMotorTargetSpeed(speed, direction)
