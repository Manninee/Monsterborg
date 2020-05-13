import os
import numpy as np

import datainput

files = os.scandir("Data")
frames = 0
filenames = []
for i in files:
    if not i.name.endswith(".avi"):
        continue

    # Get video name without file extension
    name = i.name.split(".")[0]

    frames += datainput.frameCount(name)
    filenames.append(name)

# File names for arrays
imagesFileName = "C:\\images.dat"
commandsFileName = "C:\\commands.dat"

imagesFile = np.memmap(imagesFileName, dtype='float32', mode="w+", shape=(frames, 190, 480, 3))
commandsFile = np.memmap(commandsFileName, dtype='float32', mode="w+", shape=(frames, 3))

index = 0
for i in filenames:
    images, commands = datainput.readData(i, 3)
    oneHotEncoded = np.eye(3)[commands]

    end = index + len(images)

    imagesFile[index: end] = images
    commandsFile[index: end] = oneHotEncoded

    index = end + 1

    imagesFile.flush()
    commandsFile.flush()

print("Done")
