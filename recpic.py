from config import *
import cv2
import numpy as np
import base64
import skimage.io

src = r'C:\Users\moxu\Pictures\ammunition.jpg'
img = cv2.imread(src)
# for i in range(img.shape[0]):
#     for j in range(img.shape[1]):
#         if np.sum(img[i, j]) > 750:
#             img[i, j] = [0, 0, 0]
# img = cv2.resize(img[30: 190, 30: 190], (160, 160))
# cv2.circle(img, (80, 80), 73, (50,205,50), 5)

print(img.shape)
img = cv2.resize(img, (50, 50))
for i in range(50):
    for j in range(50):
        if (i - 25) ** 2 + (j - 25) ** 2 > 22 ** 2:
            img[i, j] = (0, 0, 0)
# img = cv2.resize(img[: 2400,: 1500], (500, 800))
# cv2.imwrite(r'C:\Users\moxu\Pictures\boss3.png', img)
# with open(src, "rb") as f:
#     # b64encode是编码，b64decode是解码
#     base64_data = base64.b64encode(f.read())
#     # print(base64_data)  # 输出生成的base64码
#
# with open("code.txt", "w") as f:
#     f.write(str(base64_data))
# #
# img = base64.b64decode(base64_data)
# # print(img.shape)
# file = open('timg.png', "wb")
# file.write(img)
#
# img = skimage.io.imread(img, plugin='imageio')
# img = cv2.resize(img, (250, 250))
# #
#

#
# for i in range(img.shape[0] - 20, img.shape[0]):
#     for j in range(img.shape[1]):
#         if np.sum(img[i, j]) > 600:
#             img[i, j] = [0, 0, 0]

with open('1.txt', 'w') as f:
    f.write(str(list(img)))
# print(img.shape)
# with open('001.png', 'wb') as f:
#     f.write(img)
#
# src = 'C:/Users/moxu/Pictures/bg2.jpg'
# img = cv2.imread(src)
#
# # 逆时针以图像中心旋转-90度图像
#
# print(img.shape)

# img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
# img = cv2.resize(img, (500, 800))
# cv2.imwrite('pics/bg.png', img)
cv2.imshow('img', img)
cv2.waitKey()
# txt = './1.txt'
# file = open(txt, 'w')
# file.write(str(list(img)))
