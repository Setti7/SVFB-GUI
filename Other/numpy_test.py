import numpy as np
import os, random, time

file = "numpy_test.npy"

if os.path.exists(file):
    data = np.load(file)

else:
    data = np.empty(shape=[0,2]) # Creates an empty 2d array

for i in range(1000):
    n1 = random.randint(0,10)
    n2 = random.randint(0,10)
    number_array = np.array([[n1, n2]])

    data = np.concatenate((data, number_array))

np.save(file, data)
print(data)
print(data.shape)