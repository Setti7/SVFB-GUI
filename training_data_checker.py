import numpy as np
import sys, os

def clear(*args):
    """
    The parameters need to be the file paths. Ex: "example_folder\\file.txt"
    """
    for file in args:
        np.save(file, np.empty(shape=[0,2]))

dataf = "Data\\frames.npy"
framesf = 'Data\\training_data.npy'

data = np.load(dataf)
frames = np.load(framesf)

# frames = [array[0] for array in file]
# choices = [array[1] for array in file]
#

print(data)
print(frames)

# clear(dataf, framesf)
# print(len(frames))
# print(len(choices))

