import threading
from time import sleep
from datetime import datetime
import cv2
import numpy as np


class SavingThread(threading.Thread):
    def __init__(self, save, imageQueue, commandQueue):
        threading.Thread.__init__(self)
        self.end = False
        self.imageQueue = imageQueue
        self.commandQueue = commandQueue
        self.save = save
        self.interval = 0.1

        self.txtWriter = None
        self.videoWriter = None

        self.saving = False
        self.videoFps = 20.0
        self.videoResolution = (480, 360)

    def run(self):
        while True:
            self.save.wait()
            if self.end:
                break
            sleep(self.interval)

            if self.save.is_set() and not self.saving:
                # Start recording commands and video
                time = datetime.now().strftime("%H%M%S")
                self.txtWriter = open(time + ".txt", "w")
                fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
                self.videoWriter = cv2.VideoWriter(time + ".avi", fourcc,
                                                   self.videoFps, self.videoResolution)
                self.saving = True

            elif self.save.is_set():
                # Save commands
                while not self.commandQueue.empty():
                    self.txtWriter.write(self.commandQueue.get())
                    self.txtWriter.write("\n")

                # Save video frames
                while not self.imageQueue.empty():
                    self.videoWriter.write(cv2.cvtColor(np.array(self.imageQueue.get()), cv2.COLOR_RGB2BGR))

            elif self.saving:
                # Stop recording
                self.saving = False
                self.txtWriter.close()
                self.txtWriter = None
                self.videoWriter.release()
                self.videoWriter = None

        print("Saving end")

    def stop(self):
        if self.txtWriter:
            self.txtWriter.close()
        if self.videoWriter:
            self.videoWriter.release()
        self.end = True
