import numpy as np
import cv2


image = cv2.imread(r'/root/cv-0-7/project/asset/data/fruits.jpg')
# image = cv2.imread(r'projects/OpenCV2/task_6/task_6/asset/data/fruits.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# INSERT STUDENT CODE HERE

image_scaled_test = cv2.resize(image, None, fx=0.75, fy=0.75)

image_scaled_np = np.array(image_scaled)
image_scaled_test_np = np.array(image_scaled_test)

are_images_identical = np.array_equal(image_scaled_np, image_scaled_test_np)

if are_images_identical:
    print(1)
else:
    print(0)