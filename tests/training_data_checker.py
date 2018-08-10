import numpy as np
import os, cv2

# for file in os.listdir('Data\\test-res'):
#     file_path = os.path.join('Data\\test-res', file)
#     print("Opening: %s" % file_path)
#     training_data = np.load(file_path)
#
#     frames = [array[0] for array in training_data]
#     choices = [array[1] for array in training_data]
#
#     # Getting the shape of the first frame (All frames should have the same size), but I don't know if different
#     # captures have. So compare this.
#     img = training_data[0][0][7:137]
#     print(img.shape[::-1])
#     for data in training_data:
#         img = data[0][7:137]
#         # choice = data[1]
#         cv2.imshow('Training data', img)
#
#         # print(choice)
#         if cv2.waitKey(25) & 0xFF == ord('q'):
#             cv2.destroyAllWindows()
#             exit()

MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
os.chdir(MAIN_DIR)

training_data_s1 = np.load('Data/Training Data/c25dcb81-e639-44ef-a5bd-9e3408c4a84d.npy')

while True:

    last_frame_s1 = training_data_s1[-1][0]

    cv2.imshow('Screen', last_frame_s1)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        exit()