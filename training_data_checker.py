import numpy as np
import\
    os, cv2

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

# Returns rect coordinates
def find_rect(img):
    pass

# Return fish coordinates
def find_fish(img):
    pass


training_data_s1 = np.load('Data/test-res/training_data.npy')
training_data_s2 = np.load('Data/test-res/training_data_FRNXZLG.npy')

training_data_f1 = np.load('Data/test-res/training_data_sb7I9xj.npy')
training_data_f2 = np.load('Data/test-res/training_data_y2ZGzZj.npy')

while True:

    last_frame_s1 = training_data_s1[-1][0]
    last_frame_s2 = training_data_s2[-1][0]

    last_frame_f1 = training_data_f1[-1][0]
    last_frame_f2 = training_data_f2[-1][0]

    edges_s = cv2.Canny(last_frame_s1, 100, 200)
    edges_f = cv2.Canny(last_frame_f1, 100, 200)

    # For adaptative threshold, blurring is nice
    blur_s1 = cv2.medianBlur(last_frame_s1, 5)
    blur_s2 = cv2.medianBlur(last_frame_s2, 5)
    blur_f1 = cv2.medianBlur(last_frame_f1, 5)
    blur_f2 = cv2.medianBlur(last_frame_f2, 5)

    thresh_s1 = cv2.adaptiveThreshold(blur_s1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh_s2 = cv2.adaptiveThreshold(blur_s2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh_f1 = cv2.adaptiveThreshold(blur_f1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh_f2 = cv2.adaptiveThreshold(blur_f2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    cv2.imshow('Success 1', thresh_s1)
    cv2.imshow('Success 2', thresh_s2)
    cv2.imshow('Failure 1', thresh_f1)
    cv2.imshow('Failure 2', thresh_f2)

    if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                exit()