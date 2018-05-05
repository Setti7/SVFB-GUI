import numpy as np
import sys, os

file_name = "Data\\training_data.npy"

file = np.load(file_name)

frames = [array[0] for array in file]
choices = [array[1] for array in file]

print(len(file))
print(len(frames))
print(len(choices))