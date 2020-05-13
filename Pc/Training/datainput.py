import cv2
import numpy as np


def readData(filename, channels=1):
    cap = cv2.VideoCapture("./Data/" + filename + ".avi")
    error = 0
    while not cap.isOpened():
        cap = cv2.VideoCapture("./Data/" + filename + ".avi")
        cv2.waitKey(100)
        error += 1
        if error == 20:
            print("Could not find file")
            return [], []

        print("Wait for the header")

    text = open("./Data/" + filename + ".txt")

    frames = []
    commands = []
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    while True:
        flag, frame = cap.read()
        if flag:
            command = text.readline()
            if "w" in command:
                frame = frame[170:, :]
                if channels == 1:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    frame = frame.reshape(frame.shape[0], frame.shape[1], 1)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                frame = frame.astype('float32') / 255
                frames.append(frame.copy())

                if "a" in command:      # wa
                    commands.append(0)
                elif "d" in command:    # wd
                    commands.append(1)
                else:                   # w
                    commands.append(2)
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
            cv2.waitKey(10)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            break

    return frames, commands


def frameCount(filename):
    # Count the amount of valid image commands pairs

    cap = cv2.VideoCapture("./Data/" + filename + ".avi")
    error = 0
    while not cap.isOpened():
        cap = cv2.VideoCapture("./Data/" + filename + ".avi")
        cv2.waitKey(100)
        error += 1
        if error == 20:
            print("Could not find file")
            return -1

    text = open("./Data/" + filename + ".txt")

    frames = 0
    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    while True:
        flag, frame = cap.read()
        if flag:
            command = text.readline()
            if "w" in command:
                frames += 1
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
            cv2.waitKey(10)

        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            break

    return frames
