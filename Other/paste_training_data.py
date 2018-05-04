import numpy as np
import sys, os

parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
complete_file_path = os.path.join(parent_folder, "Data\\training_data.npy")
file_name = complete_file_path

file = np.load(file_name)
np.save(file_name, np.array([[10,2,3], [12,53,12], [12,63,15]]))
loaded = np.load(file_name)
print(loaded)

loaded = np.vstack((loaded, [1,24,4]))
print(loaded)

#
# np.save("tests", np.array([[1, 20], [2,4]]))
# for array in np.load('tests.npy'):
#     print(array)
# print(file2)