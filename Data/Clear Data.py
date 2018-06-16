import numpy as np

def clear(*args):
    """
    The parameters need to be the file paths. Ex: "example_folder\\file.txt"
    """
    for file in args:
        np.save(file, np.empty(shape=[0,2]))

clear("frames.npy", 'training_data.npy', 'data.npy')