import numpy as np
import cv2


image = cv2.imread(r'/root/cv-0-7/project/asset/data/fruits.jpg')
# image = cv2.imread(r'projects/OpenCV2/task_6/task_6/asset/data/fruits.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# INSERT STUDENT CODE HERE

img_scaled_test = cv2.resize(image, None, fx=2, fy=2, interpolation = cv2.INTER_CUBIC)

img_scaled_np = np.array(img_scaled)
img_scaled_test_np = np.array(img_scaled_test)

are_images_identical = np.array_equal(img_scaled_np, img_scaled_test_np)

if are_images_identical:
    print(1)
else:
    print(0)