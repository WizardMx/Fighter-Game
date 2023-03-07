import random
import time
import numpy as np
import cv2
from config import *
from sticker import *

import base64, skimage.io

class Info(object):
    def __init__(self):
        self.ST = time.time()
        self.points = 0
        self.life = fighterStartLife
        self.fireLevel = 0
        self.fireLaserLevel = 1
        self.fireMissileLevel = 0
        self.fireLasersLevel = 0
        self.color = [0, 1, 2]
        self.halo = None
        self.stickerbackup = None
        self.specialfighter = 0

    def reset(self):
        self.ST = time.time()
        self.points = 0
        self.life = fighterStartLife
        self.fireLevel = 0
        self.fireLaserLevel = 1
        self.fireMissileLevel = 0
        self.fireLasersLevel = 0
        self.color = [0, 1, 2]
        self.halo = None
        self.stickerbackup = None
        self.specialfighter = 0

    def sethalo(self, color, last, ST):
        self.halo = {'color': color, 'last': last, 'ST': ST}

    def updatePoint(self, point):
        self.points += point

    def updateLife(self, life):
        self.life += life

    def display(self, board, lastPoint, lastLife):

        bar1 = np.ones((25, 360, 3))
        bar1[:, :] = (12, 12, 24)
        bar1[:, :int(bar1.shape[1] / fighterStartLife * self.life)] = (34, 139, 34)
        board[0: 25, 70: 430] = bar1
        cv2.rectangle(board, (70, 0), (430, 25), (213, 239, 255), 2)
        cv2.putText(board, '{}'.format(self.life), (240, 20), cv2.FONT_ITALIC, 0.7, (0, 140, 255), 2)

        cv2.rectangle(board, (430, 0), (500, 30), (213, 239, 255), 2)
        cv2.rectangle(board, (0, 0), (70, 30), (213, 239, 255), 2)
        cv2.putText(board, '{}'.format(self.points), (432, 24), cv2.FONT_ITALIC, 0.8, (0, 215, 255), 2)
        scs = int(time.time() - self.ST)
        cv2.putText(board, '{}:{}'.format(scs // 60, scs % 60), (10, 20), cv2.FONT_ITALIC, 0.6, (204, 50, 153), 2)

        return self.points, self.life


def fancy_fighter(size=50, flip=1, color=[2, 0, 1], color_seed=0):
    img = np.array(Fighter1)
    color = np.array(color).astype(np.uint8)
    if len(color) == 4:
        color_seed = color[3]

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if np.sum(img[i, j]) > 300:
                img[i, j] += color_seed

    img = cv2.resize(img, (size, int(1.8 * size))).astype(np.uint8)
    img = cv2.flip(img, flip)
    return img[:, :, color[: 3]]


def fancy_fighter_1(size=50, flip=1):
    img = np.array(Fighter2)
    img = cv2.resize(img, (size, int(1.5 * size)))
    img = cv2.flip(img, flip)
    return img


def fighter(size, flip=None):
    color = (0, 255, 255)
    if flip is not None:
        color = (0, 0, 255)
    canvas_size = 3 * size
    canvas = np.zeros((canvas_size, canvas_size, 3))
    cv2.line(canvas, (canvas_size // 2 - (size - canvas_size // 2), 2 * size), (canvas_size // 2, 2 * size), color)
    cv2.line(canvas, (canvas_size // 2, 2 * size), (size, 2 * size), color)
    cv2.line(canvas, (canvas_size // 2, 2 * size), (canvas_size // 2, 0), color)
    cv2.line(canvas, (size, size), (size, 2 * size), color)
    cv2.line(canvas, (2 * size, size), (2 * size, 2 * size), color)
    cv2.line(canvas, (canvas_size // 2, 0), (size, size), color)
    cv2.line(canvas, (canvas_size // 2, 0), (2 * size, size), color)
    cv2.line(canvas, (size - size // 2, 2 * size), (2 * size + size // 2, 2 * size), color)
    cv2.line(canvas, (size - size // 2, 2 * size), (size, 2 * size - size // 2), color)
    cv2.line(canvas, (2 * size + size // 2, 2 * size), (2 * size, 2 * size - size // 2), color)

    temp = canvas[: 2 * size + 2, size // 3: size // 3 * 8].copy()
    if flip is not None:
        temp = cv2.flip(temp, -1)
    return temp

def bullet(size):
    canvas = np.zeros((size, size, 3)).astype(np.uint8)
    cv2.circle(canvas, (size // 2, size // 2), size // 2, (random.randint(0, 55), random.randint(0, 55), random.randint(200, 255)), thickness=-1)
    cv2.circle(canvas, (size // 2, size // 2), size // 3, (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255)), thickness=2)
    return canvas

def bullet_laser(size, width=4):
    canvas = (np.random.rand(size, width, 3) * 256).astype(np.uint8)
    return canvas

def bullet_missile(size, color=[0, 1, 2]):
    canvas = Missile
    canvas = cv2.resize(canvas, (size, size*4))
    return canvas[:, :, color]

def laserIcon(size=20):
    canvas = LaserIcon
    canvas = cv2.resize(canvas, (size, size))
    return canvas

def boom0():
    img_data = Boom
    img = base64.b64decode(img_data)
    img = skimage.io.imread(img, plugin='imageio')
    img = img[:, :, [2, 1, 0]]

    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            if np.sum(img[i, j]) > 764:
                img[i, j] = [0, 0, 0]
    return img[: 180, 30: 250]

Boom = boom0()
def boom(size):
    # temp = np.zeros((size, size, 3)).astype(np.uint8)
    # canvas = np.random.rand(size, size, 3) * 256
    #
    # temp[size // 2 - size // 2: size // 2 + size // 2, size // 2 - size // 2: size // 2 + size // 2] = \
    #     (np.maximum((canvas[size // 2 - size // 2: size // 2 + size // 2,
    #                  size // 2 - size // 2: size // 2 + size // 2] - 250), 0) / 6 * 256).astype(np.uint8)
    #
    # temp[size // 2 - size // 3: size // 2 + size // 3, size // 2 - size // 3: size // 2 + size // 3] = \
    #     (np.maximum((canvas[size // 2 - size // 3: size // 2 + size // 3,
    #                  size // 2 - size // 3: size // 2 + size // 3] - 220), 0) / 36 * 256).astype(np.uint8)
    #
    # temp[size // 2 - size // 4: size // 2 + size // 4, size // 2 - size // 4: size // 2 + size // 4] = \
    #     (np.maximum((canvas[size // 2 - size // 4: size // 2 + size // 4,
    #                  size // 2 - size // 4: size // 2 + size // 4] - 200), 0) / 56 * 256).astype(np.uint8)

    img = Boom.copy()
    img = cv2.resize(img, (size, size))
    # cv2.imshow('img', img)
    # cv2.waitKey()
    return img

def background0():
    img_data = Background1
    img = base64.b64decode(img_data)
    img = skimage.io.imread(img, plugin='imageio')
    return img

bgd = background0()
def background(size = (800, 500)):

    img = bgd.copy()
    # img = img[:, :, [2, 1, 0]]
    img = cv2.rotate(cv2.resize(img, size[: 2]), 2)
    return img.astype(np.uint8)

def boss1starter():
    img_data = Boss1
    img = base64.b64decode(img_data)
    img = skimage.io.imread(img, plugin='imageio')
    return img

boss1_ = boss1starter()
def boss1(size = 250):

    img = cv2.resize(boss1_, (size, size))
    return img[:, :, [2, 1, 0]]

def boss2starter():
    img_data = Boss2
    img = base64.b64decode(img_data)
    img = skimage.io.imread(img, plugin='imageio')
    return img

boss2_ = boss2starter()
def boss2(size = 250):

    img = cv2.resize(boss2_, (size, size))
    return img[:, :, [2, 1, 0]].copy()

def boss3starter():
    img_data = Boss3
    img = base64.b64decode(img_data)
    img = skimage.io.imread(img, plugin='imageio')
    return img

boss3_ = boss3starter()
def boss2Hit(size = 250):

    img = cv2.resize(boss3_, (size, size))
    return img[:, :, [2, 1, 0]].copy()


def ufo(size):
    img = cv2.resize(Ufo, (int(size/72*176)-1, size))
    return img

def bufferHP(size = 20):
    img = cv2.resize(RecoverIcon, (size, size))
    return img

def ammunitionIcon(size = 20):
    img = cv2.resize(IconAmmunition, (size, size))
    return img

# b = np.vstack((background(), background()))
# print(b.shape)
# h = 0
# cv2.imshow('img0', background()[0: 800])
# cv2.waitKey()
# cv2.imshow('img1', b[0: 800])
# cv2.waitKey()
# cv2.imshow('img2', b[800: 1600])
# cv2.waitKey()
# while True:
#     print(h, h+800)
#     cv2.imshow('img', b[h: h+800])
#     cv2.waitKey(10)
#     h = (h - 1) % 801
#
# f = boss2Hit()
# print(f.shape)
# cv2.imshow('canvas', f)
# cv2.waitKey()
# b = bullet_missile(30, [0, 1, 2])
# print(b.shape)
#
# cv2.imshow('canvas', b)
# cv2.waitKey()
# b = boom(100)
# cv2.imshow('canvas', b)
# cv2.waitKey()
