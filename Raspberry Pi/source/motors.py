from source import ThunderBorg
import threading
from time import sleep


class MotorSpeedControlThread(threading.Thread):
    def __init__(self, end):
        threading.Thread.__init__(self)
        self.end = end

        self.leftTargetSpeed = 0
        self.rightTargetSpeed = 0
        self.targetValuesLock = threading.Lock()

        self.TB = ThunderBorg.ThunderBorg()
        self.TB.Init()

        if not self.TB.foundChip:
            raise Exception('could not detect ThunderBorg')

        self.TB.SetCommsFailsafe(False)  # Disable the communications fail safe
        self.TB.MotorsOff()
        self.TB.SetLedShowBattery(False)
        self.TB.SetLeds(0, 0, 0.15)

        self.motorMaxValue = 0.8

        # Constants to define motor control loop behaviour
        self.step = self.motorMaxValue / 10
        self.interval = 0.025

        self.currentSpeeds = [0, 0]

    def run(self):
        while not self.end.is_set():
            sleep(self.interval)
            values = self.getMotorTargetSpeed()
            for i in range(2):
                difference = values[i] - self.currentSpeeds[i]
                if abs(difference) > 0:
                    # Change current motor speeds closer to target speeds
                    if abs(difference) < self.step:
                        self.currentSpeeds[i] = values[i]
                    elif difference > 0:
                        self.currentSpeeds[i] += self.step
                    else:
                        self.currentSpeeds[i] -= self.step

            self.TB.SetMotor1(self.currentSpeeds[0])
            self.TB.SetMotor2(self.currentSpeeds[1])

        print("Motors end")
        self.TB.MotorsOff()
        self.TB.SetLedShowBattery(True)

    def getMotorMaxValue(self):
        return self.motorMaxValue

    def setMotorTargetSpeed(self, speed, direction):
        speed *= self.motorMaxValue

        # Calculate motors speeds for inside and outside motors
        speedRatio = (self.motorMaxValue - abs(speed)) / 2
        speedInside = speed * (1 - abs(direction) * (1 - (0.10 * (1 - speedRatio))))
        speedOutside = speed * (1 + speedRatio * abs(direction) * 1.1)

        if direction > 0:
            left = speedInside
            right = speedOutside
        elif direction < 0:
            left = speedOutside
            right = speedInside
        else:
            left = speed
            right = speed

        self.targetValuesLock.acquire()
        self.leftTargetSpeed = left
        self.rightTargetSpeed = right
        self.targetValuesLock.release()

    def getMotorTargetSpeed(self):
        self.targetValuesLock.acquire()
        left = self.leftTargetSpeed
        right = self.rightTargetSpeed
        self.targetValuesLock.release()
        return [left, right]
