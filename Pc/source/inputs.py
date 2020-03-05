import threading
import pygame


class InputsThread(threading.Thread):
    def __init__(self, udpQueue, udpEvent, save, saveQueue):
        threading.Thread.__init__(self)
        self.end = False
        self.queue = udpQueue
        self.event = udpEvent
        self.save = save
        self.saveQueue = saveQueue

        self.pressedKeys = set(())
        self.joystick = None

        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() < 1:
            pygame.joystick.quit()
            print("no joysticks")
        else:
            print(pygame.joystick.get_count(), "joysticks")
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.axes = self.joystick.get_numaxes()
            self.buttons = self.joystick.get_numbuttons()

    def run(self):
        while not self.end:
            self.event.wait()
            command = self.getKeyboardData() + ";"

            if self.joystick:
                command += self.getControllerData()

            self.queue.put(command)
            self.event.clear()

            if self.save.is_set():
                self.saveQueue.put(command)

        print("Inputs end")

    def getKeyboardData(self):
        return ",".join(self.pressedKeys)

    def getControllerData(self):
        data = []
        pygame.event.get()
        for i in range(self.axes):
            data.append(str(round(self.joystick.get_axis(i), 3)))

        for i in range(self.buttons):
            data.append(str(self.joystick.get_button(i)))

        return ",".join(data)

    def addKey(self, key):
        self.pressedKeys.add(key)

    def removeKey(self, key):
        self.pressedKeys.discard(key)

    def stop(self):
        self.end = True
