import numpy as np
import sys, os, cv2

framesf = "Data\\frames.npy"
training_data = 'Data\\training_data.npy'

training_data = np.load(training_data)
frames = np.load(framesf)

frames = [array[0] for array in training_data]
choices = [array[1] for array in training_data]

for data in training_data:
    img = data[0]
    choice = data[1]
    print(img.shape[::-1])
    cv2.imshow('Training data', img)
    print(choice)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        exit()