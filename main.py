import os
import copy
import cv2
import numpy as np
import random
import time
# import keyboard
from pics import *
from config import *
from tools import *
class object(object):
    def __init__(self, type, sticker, pos, hp = None, damage = None, generated = None, holdback = 40, speed = None):
        self.type = type
        self.sticker = sticker
        self.pos = np.array(pos).astype(float)
        self.hp = hp
        self.maxHp = hp
        self.damage = damage
        self.holdback = holdback
        self.exist = True
        self.bornTime = None
        self.generated = False
        self.lastFire = None
        self.numFire = 0
        self.speed = speed
        self.lastHit = None

        if self.type == 'boom' or 'bullet-missile':
            self.bornTime = time.time()

objs = []
info = Info()

def LocateCentre(board, obj, pos = None):

    H, W, _ = board.shape
    h, w, _ = obj.shape

    y = H - h if pos is None else H - h - pos # offset upward
    board[y : y + h, W // 2 - w // 2 : W // 2 + w // 2] = obj

def LocateGUI(board, obj, pos):

    H, W, _ = board.shape
    h, w, _ = obj.shape

    offHor, offVer = pos
    offHor = int(offHor)
    offVer = int(offVer)
    y = H - h - offVer

    if y < 0 or y + h > H or W // 2 - w // 2 + offHor < 0 or W // 2 + w // 2 + offHor > W:
        return False

    adj = 1 if w % 2 else 0

    board[y: y + h, W // 2 - w // 2 + offHor: W // 2 + w // 2 + offHor + adj] = \
        obj.copy()

    return True

def Locate(board, obj, pos, hp = None, maxhp = enemyHp['enemy'], ps = None):

    H, W, _ = board.shape
    h, w, _ = obj.shape

    offHor, offVer = pos
    offHor = int(offHor)
    offVer = int(offVer)
    y = H - h - offVer

    if ps == 'tell me where out':
        if y + h > H:
            return 'bottom out'

    if y < 0 or y + h > H or W // 2 - w // 2 + offHor < 0 or W // 2 + w // 2 + offHor > W:
        return False

    adj = 1 if w % 2 else 0

    board[y: y + h, W // 2 - w // 2 + offHor: W // 2 + w // 2 + offHor + adj] = \
        np.maximum(obj.copy(), board[y: y + h, W // 2 - w // 2 + offHor: W // 2 + w // 2 + offHor + adj])
    if hp is not None:
        bar = np.ones(board[y - 5: y - 1, W // 2 - w // 2 + offHor: W // 2 + w // 2 + offHor + adj].shape)
        bar[:, :min(int(w * hp / maxhp), w-1)] = (0, 255, 0)
        board[y - 5: y - 1, W // 2 - w // 2 + offHor: W // 2 + w // 2 + offHor + adj] = bar

    return True


def ifLocate(board, obj, pos):

    H, W, _ = board.shape
    h, w, _ = obj.shape

    offHor, offVer = pos.copy().astype(int)
    y = H - h - offVer

    if y < 0 or y + h > H or W // 2 - w // 2 + offHor < 0 or W // 2 + w // 2 + offHor > W:
        return False

    adj = 1 if w % 2 else 0

    return np.sum(board[y: y + h, W // 2 - w // 2 + offHor: W // 2 + w // 2 + offHor + adj]) < 1

def fire(board):
    temp = bullet(fireSize)
    temp_pos = objs[0].pos.copy()
    temp_pos[1] += objs[0].sticker.shape[1]
    #
    objs.append(object('bullet', temp.copy(), temp_pos.copy(), damage=fireDamage))
    _ = Locate(board, temp, temp_pos)
    bullets = ['bulletl1', 'bulletr1', 'bulletl2', 'bulletr2', 'bulletl3', 'bulletr3']
    for i in range((info.fireLevel - 1) * 2):
        # print(bullets[i])
        objs.append(object(bullets[i], temp.copy(), temp_pos.copy(), damage=fireDamage))

def fireMissile(board, adj = 0):
    temp = bullet_missile(fireSize)
    temp_pos = objs[0].pos.copy()
    temp_pos[0] += objs[0].sticker.shape[0] // 6
    objs.append(object('bullet-missile', temp.copy(), temp_pos.copy(), damage=fireMissileDamage))
    objs[-1].bornTime -= adj
    if adj:
        objs[-1].generated = True
    _ = Locate(board, temp, temp_pos)

    temp = bullet_missile(fireSize)
    temp_pos = objs[0].pos.copy()
    temp_pos[0] -= objs[0].sticker.shape[0] // 6
    objs.append(object('bullet-missile', temp.copy(), temp_pos.copy(), damage=fireMissileDamage))
    objs[-1].bornTime -= adj
    if adj:
        objs[-1].generated = True
    _ = Locate(board, temp, temp_pos)
    # _ = Locate(board, objs[0].sticker, objs[0].pos)

def fireLaser(board):
    temp = bullet_laser(fireLaserSize)
    temp_pos = objs[0].pos.copy()
    temp_pos[1] += objs[0].sticker.shape[1]
    objs.append(object('bullet-laser', temp, temp_pos, damage=fireLaserDamage))
    flag = Locate(board, temp, temp_pos)
    if not flag:
        objs.pop()

def fireLasers(board):
    temp_pos = objs[0].pos.copy()
    temp_pos[1] += objs[0].sticker.shape[1]
    temp = bullet_laser(int(800 - 1 - temp_pos[1]), 1)
    temp2 = (np.ones(bullet_laser(int(800 - 1 - temp_pos[1]), 5).shape) * 255).astype(np.uint8)
    objs.append(object('bullet-lasers', [temp, temp2], temp_pos, damage=fireLasersDamage, holdback=3))
    flag = Locate(board, temp, temp_pos)
    if not flag:
        objs.pop()

def firefly(board, bullet, speed=(0, 5), damage = 24):
    # _ = Locate(board, np.zeros(bullet.sticker.shape), bullet.pos)
    # print(bullet.pos, speed)
    bullet.pos[0] += speed[0]
    bullet.pos[1] += speed[1]

    sticker = bullet.sticker
    if bullet.type == 'bullet-lasers' and damage == 0:
        # bullet.pos = objs[0].pos.copy()
        # bullet.pos[1] += objs[0].sticker.shape[1]
        factor = int((time.time() - bullet.bornTime) / 0.1)
        sticker = cv2.resize(sticker[0], (sticker[0].shape[1] * (factor + 1), sticker[0].shape[0]))

    if bullet.type == 'bullet-lasers' and damage != 0:
        # bullet.pos = objs[0].pos.copy()
        # bullet.pos[1] += objs[0].sticker.shape[1]
        sticker = sticker[1]

    flag = Locate(board, sticker, bullet.pos)
    if bullet.type == 'bullet-missile':
        if time.time() - bullet.bornTime < 1:
            flag = True
    if not flag:
        return flag
    for i, enemy in enumerate(objs):
        if ('enemy' not in enemy.type and 'attack' not in enemy.type) or enemy.exist is False:
            continue
        # print(enemy.sticker.shape, bullet.sticker.shape)
        # print(get_box(enemy.pos, enemy.sticker.shape), get_box(bullet.pos, bullet.sticker.shape))
        if is_box_intersect(get_box(enemy.pos, enemy.sticker.shape), get_box(bullet.pos, sticker.shape)):

            if 'enemy' in enemy.type:
                enemy.hp -= damage
                if enemy.hp <= 0:
                    objs.append(object('boom', boom(enemySize), enemy.pos))
                    if enemy.type == 'enemy' and random.random() > 0.3:
                        objs.append(object('buff-HP', bufferHP(20), enemy.pos, speed=fireSpeed['buff']))
                    if enemy.type == 'enemy-ufo':
                        if random.random() > 0.5:
                            objs.append(object('buff-LU-mi', cv2.rotate(bullet_missile(8, [1, 1, 2]), 0), enemy.pos, speed=fireSpeed['buff0']))
                        else:
                            objs.append(object('buff-LU-la', laserIcon(), enemy.pos, speed=np.array(fireSpeed['buff0'])))

                        objs.append(object('buff-LU', ammunitionIcon(), enemy.pos, speed=np.array(fireSpeed['buff'])))
                        info.specialfighter -= 1

                    info.updatePoint(enemyPoints[enemy.type])
                    enemy.exist = False

                else:
                    if damage:
                        enemy.pos[1] -= enemyMoveSpeed[enemy.type][1] * bullet.holdback
                    if bullet.type == 'bullet-missile':
                        objs.append(object('boom', boom(enemySize*2), enemy.pos))
                    _ = Locate(board, enemy.sticker, enemy.pos)

            if enemy.type == 'enemy-ufo':
                enemy.lastHit = time.time()
                enemy.sticker = boss2Hit()
                enemy.pos += np.array([random.randint(-5, 5), random.randint(-5, 5)])

            if 'attack' in enemy.type:
                if damage:
                    objs.append(object('boom', boom(enemySize), enemy.pos))
                    enemy.exist = False

            if bullet.type != 'bullet-lasers':
                objs.remove(bullet)
                break

    return flag

def antifirefly(board, bullet, speed=(0, 5), damage = 24):

    bullet.pos[0] += speed[0]
    bullet.pos[1] += speed[1]

    flag = Locate(board, bullet.sticker, bullet.pos)

    if not flag:
        return flag

    if is_box_intersect(get_box(objs[0].pos, objs[0].sticker.shape), get_box(bullet.pos, bullet.sticker.shape)):
        flag = False
        objs.append(object('boom', boom(bullet.sticker.shape[0])[:, :, [2, 0, 1]], bullet.pos))
        info.updateLife(-damage)

    return flag

def antifriendlyfirefly(board, bullet, speed=(0, 5), damage = 24):

    bullet.pos[0] += speed[0]
    bullet.pos[1] += speed[1]

    flag = Locate(board, bullet.sticker, bullet.pos, ps = 'tell me where out')

    exist = False
    flip = False
    if flag == 'bottom out':
        return exist, flip

    if flag is False:
        flip = True

    exist = True
    if is_box_intersect(get_box(objs[0].pos, objs[0].sticker.shape), get_box(bullet.pos, bullet.sticker.shape)):
        exist = False
        if bullet.type == 'buff-HP':
            info.life = min(info.life + 10, fighterStartLife)
            info.sethalo([2, 0, 1, 50], 1, time.time())
        if bullet.type == 'buff-LU':
            if info.fireLevel == 0:
                cv2.putText(board, 'New weapon: Cannon (J)', (90, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
            else:
                cv2.putText(board, 'Cannon Level Up !', (120, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
            cv2.imshow('fighter', board)
            cv2.waitKey()
            info.fireLevel = min(info.fireLevel + 1, 4)
            info.sethalo([1, 0, 2, 100], 1, time.time())
        if bullet.type == 'buff-LU-mi':
            if info.fireMissileLevel == 0:
                cv2.putText(board, 'New weapon: Cannon (K)', (90, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
            else:
                cv2.putText(board, 'Missile Level Up !', (120, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
            cv2.imshow('fighter', board)
            cv2.waitKey()
            info.fireMissileLevel = min(info.fireMissileLevel + 1, 4)
            info.sethalo([1, 0, 2, 100], 1, time.time())
        if bullet.type == 'buff-LU-la':
            if info.fireLasersLevel == 0:
                cv2.putText(board, 'New weapon: Laser (L)', (90, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
            else:
                cv2.putText(board, 'Laser Level Up !', (120, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
            cv2.imshow('fighter', board)
            cv2.waitKey()
            info.fireLasersLevel = min(info.fireLasersLevel + 1, 4)
            info.sethalo([1, 0, 2, 100], 1, time.time())

    return exist, flip

def enemyAttack(idx, enemy):

    for i, fighter in enumerate(objs):
        if i == idx or objs[i].type == 'boom' or objs[i].type == 'enemy-ufo' or objs[i].type == 'enemy-round' \
                or 'bullet' in objs[i].type or 'attack' in objs[i].type or 'buff' in objs[i].type:
            continue
        fighter = objs[i]
        if is_box_intersect(get_box(enemy.pos, enemy.sticker.shape), get_box(fighter.pos, fighter.sticker.shape)):
            # if 'buff' in fighter.type:
            #     objs.remove(fighter)
            #     continue
            objs.append(object('boom', boom(enemy.sticker.shape[0]), enemy.pos.copy()))
            boomPos = enemy.pos.copy()
            boomPos[1] -= enemy.sticker.shape[1]
            objs.append(object('boom', boom(fighterSize), boomPos))
            if i == 0:
                info.updateLife(-30)
                return 1
            else:
                if enemy.hp != enemy.maxHp and objs[i].hp is not None:
                    objs[i].hp -= enemy.hp
                return 2
    return 0

def update(objs, board):
    print('number of objects:{}'.format(len(objs)))
    for i, obj in enumerate(objs):
        if i == 0:
            continue

        if 'attack' in obj.type:
            exist = antifirefly(board, obj, np.array(fireSpeed[obj.type]) * random.randint(1, 2), obj.damage)
            if not exist:
                objs.remove(obj)

        if obj.type in ['bullet', 'bulletl1', 'bulletr1', 'bulletl2', 'bulletr2', 'bulletl3', 'bulletr3']:
            exist = firefly(board, obj, fireSpeed[obj.type], obj.damage)
            if not exist:
                objs.remove(obj)

        if obj.type == 'bullet-laser':
            exist = firefly(board, obj, fireSpeed[obj.type], obj.damage)
            if not exist:
                objs.remove(obj)

        if obj.type == 'bullet-lasers':
            if time.time() - obj.bornTime < 0.2:
                _ = firefly(board, obj, (0, 0), 0)
            elif time.time() - obj.bornTime < 1:
                _ = firefly(board, obj, (0, 0), fireLasersDamage)
            else:
                objs.remove(obj)

        if obj.type == 'bullet-missile':
            if time.time() - obj.bornTime < 0.1:
                factor = -0.5
            elif time.time() - obj.bornTime < 1:
                factor = 0.2
            # elif time.time() - obj.bornTime < 0.6:
            #     factor = 1
            else:
                factor = 3
                # if not obj.generated:
                #     if objs[i+1].bornTime is not None and abs(obj.bornTime - objs[i+1].bornTime) < fireMissileRefill:
                #         fireMissile(board, 1)
                #     obj.generated = True
            exist = firefly(board, obj, (np.array(fireSpeed[obj.type]) * factor).astype(int), obj.damage)
            # _ = Locate(board, objs[0].sticker, objs[0].pos)
            if not exist:
                objs.remove(obj)

        if 'enemy' in obj.type:
            # _ = Locate(board, np.zeros(obj.sticker.shape), obj.pos)
            if obj.type == 'enemy-round':
                obj.pos[0] += (objs[0].pos[0] - obj.pos[0]) / 100
                obj.pos[1] += enemyMoveSpeed[obj.type][1] * 2
            else:
                obj.pos[0] += enemyMoveSpeed[obj.type][0]
                obj.pos[1] += enemyMoveSpeed[obj.type][1]
            flag = Locate(board, obj.sticker, obj.pos, obj.hp, enemyHp[obj.type])
            if not flag:
                objs.remove(obj)
                continue
            if (obj.type == 'enemy' or obj.type == 'enemy-round') and enemyAttack(i, obj):
                objs.remove(obj)

        if obj.type == 'enemy-ufo':
            interval = 3 if obj.numFire % 3 == 0 else 0.17
            if obj.lastFire is None or time.time() - obj.lastFire > interval:
                obj.lastFire = time.time()
                obj.numFire += 1
                type0 = 'attack-missile'
                sticker = cv2.flip(bullet_missile(10, [2, 0, 1]), -1)
                for i in range(1, 6):
                    type = type0 + str(i)
                    objs.append(object(type, sticker, obj.pos + np.array([20, 60]), damage=10))

            if obj.lastHit is not None and time.time() - obj.lastHit > 0.2:
                obj.sticker = boss2()
                # obj.pos = ufoPos
                obj.lastHit = None

        if obj.type == 'boom':
            _ = Locate(board, obj.sticker, obj.pos)
            if time.time() - obj.bornTime > boomLastTime:
                objs.remove(obj)

        if 'buff' in obj.type:
            exist, flip = antifriendlyfirefly(board, obj, obj.speed)
            if flip:
                obj.speed[0] *= -1
            if not exist:
                objs.remove(obj)

    for obj in objs:
        if not obj.exist:
            # if len(obj.sticker) == 2:
            #     sh = obj.sticker[0].shape
            # else:
            #     sh = obj.sticker.shape
            # _ = Locate(board, np.zeros(sh), obj.pos)
            objs.remove(obj)

import record

def GUI(board):

    backup_board = board.copy()
    locs = [[(170, 500), (330, 550)], [(170, 580), (330, 630)], [(170, 660), (330, 710)]]
    cur = 0

    while True:
        board = backup_board.copy()
        with open('D:/Fighter/highscore.txt', 'r') as file:
            hs = int(file.readline())
        cv2.putText(board, 'high score {}'.format(hs), (300, 20), cv2.FONT_ITALIC, 0.7, (255, 255, 255), 2)
        _ = Locate(board, cv2.rotate(fancy_fighter(200, color=info.color), 0), (0, 450))
        cv2.rectangle(board, locs[0][0], locs[0][1], (255, 255, 128), 2)
        cv2.rectangle(board, locs[1][0], locs[1][1], (255, 255, 128), 2)
        cv2.rectangle(board, locs[2][0], locs[2][1], (255, 255, 128), 2)

        cv2.putText(board, 'Start', (185, 540), cv2.FONT_ITALIC, 1.4, (255, 255, 255), 2)
        cv2.putText(board, 'Config', (185, 620), cv2.FONT_ITALIC, 1.4, (255, 255, 255), 2)
        cv2.putText(board, 'Color', (185, 700), cv2.FONT_ITALIC, 1.4, (255, 255, 255), 2)

        cv2.rectangle(board, locs[cur][0], locs[cur][1], (255, 0, 128), 4)
        if cur == 0:
            cv2.putText(board, 'Start', (185, 540), cv2.FONT_ITALIC, 1.4, (255, 0, 255), 2)
        if cur == 1:
            cv2.putText(board, 'Config', (185, 620), cv2.FONT_ITALIC, 1.4, (255, 0, 255), 2)
        if cur == 2:
            cv2.putText(board, 'Color', (185, 700), cv2.FONT_ITALIC, 1.4, (255, 0, 255), 2)

        cv2.putText(board, 'ESC', (5, 20), cv2.FONT_ITALIC, 0.6, (0, 0, 255), 2)

        cv2.imshow('fighter', board)
        key = cv2.waitKey()
        if key in [ord('w'), ord('W')]:
            cur = (cur - 1 + 3) % 3
        if key in [ord('s'), ord('S')]:
            cur = (cur + 1 + 3) % 3

        if key == 27:
            os._exit(0)

        if key == 13:
            if cur == 0:
                # info.fireLevel = 1
                # info.fireLasersLevel = 1
                # info.fireMissileLevel = 1
                break
            if cur == 1:
                board = np.zeros(backup_board.shape).astype(np.uint8)
                cv2.putText(board, 'Move: W, A, S, D', (100, 340), cv2.FONT_ITALIC, 0.6, (255, 0, 0), 2)
                cv2.putText(board, 'Fire: Space', (100, 360), cv2.FONT_ITALIC, 0.6, (255, 0, 0), 2)
                cv2.putText(board, 'type any key to return', (80, 400), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
                cv2.imshow('fighter', board)
                cv2.waitKey()
            if cur == 2:
                board = np.zeros(backup_board.shape).astype(np.uint8)
                cv2.putText(board, 'choose your fighter', (100, 40), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
                cv2.putText(board, 'press C for another 4', (100, 75), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
                locas = [-170, -60, 60, 170]
                colors = [[2, 1, 0], [0, 1, 2], [1, 0, 2], [0, 2, 1]]

                curcur = 0

                while True:
                    for i in range(4):
                        _ = LocateGUI(board, fancy_fighter(50, color=colors[i]), (locas[i], 100))

                    cv2.putText(board, 'A', (locas[curcur] + 245, 710), cv2.FONT_ITALIC, 0.5, (128, 64, 200), 2)
                    _ = LocateGUI(board, fancy_fighter(220, color=colors[curcur]), (0, 250))

                    cv2.imshow('fighter', board)
                    k = cv2.waitKey()

                    if k in [ord('c'), ord('C')]:
                        for i in range(4):
                            _ = LocateGUI(board, np.zeros(fancy_fighter(50).shape), (locas[i], 100))
                        for i in range(4):
                            colors[i] = [random.randint(0, 2), random.randint(0, 2), random.randint(0, 2)]
                            if i > 2:
                                colors[i].append(random.randint(-200, 200))
                    # print(colors)
                    cv2.putText(board, 'A', (locas[curcur] + 245, 710), cv2.FONT_ITALIC, 0.5, (0, 0, 0), 2)
                    if k in [ord('a'), ord('A')]:
                        curcur = (curcur - 1 + 4) % 4
                    if k in [ord('d'), ord('D')]:
                        curcur = (curcur + 1 + 4) % 4
                    if k == 13:
                        info.color = colors[curcur]
                        break

def GUI2(board):

    backup_board = board.copy()
    locs = [[(170, 500), (330, 550)], [(170, 580), (330, 630)], [(170, 660), (330, 710)]]
    cur = 0

    while True:
        board = backup_board.copy()

        _ = Locate(board, cv2.rotate(fancy_fighter(200, color=info.color), 0), (0, 450))
        cv2.rectangle(board, locs[0][0], locs[0][1], (255, 255, 128), 2)
        cv2.rectangle(board, locs[1][0], locs[1][1], (255, 255, 128), 2)
        cv2.rectangle(board, locs[2][0], locs[2][1], (255, 255, 128), 2)

        cv2.putText(board, 'Play', (185, 540), cv2.FONT_ITALIC, 1.4, (255, 255, 255), 2)
        cv2.putText(board, 'Main', (185, 620), cv2.FONT_ITALIC, 1.4, (255, 255, 255), 2)
        cv2.putText(board, 'Exit', (185, 700), cv2.FONT_ITALIC, 1.4, (255, 255, 255), 2)

        cv2.rectangle(board, locs[cur][0], locs[cur][1], (255, 0, 128), 4)
        if cur == 0:
            cv2.putText(board, 'Play', (185, 540), cv2.FONT_ITALIC, 1.4, (255, 0, 255), 2)
        if cur == 1:
            cv2.putText(board, 'Main', (185, 620), cv2.FONT_ITALIC, 1.4, (255, 0, 255), 2)
        if cur == 2:
            cv2.putText(board, 'Exit', (185, 700), cv2.FONT_ITALIC, 1.4, (255, 0, 255), 2)

        cv2.imshow('fighter', board)
        key = cv2.waitKey()
        if key in [ord('w'), ord('W')]:
            cur = (cur - 1 + 3) % 3
        if key in [ord('s'), ord('S')]:
            cur = (cur + 1 + 3) % 3

        if key == 13:
            if cur == 0:
                return
            if cur == 1:
                objs.clear()
                info.reset()
                main()
            if cur == 2:
                os._exit(0)

def game1(board, boardSize, src_highscore):
    # a = []
    # keyboard.hook(lambda x: a.append(x) if x.event_type == 'down' else x)
    # keyboard.wait(hotkey='esc')

    bg = np.vstack((background(boardSize), background(boardSize))).astype(np.uint8)
    f1 = fancy_fighter(fighterSize, color=info.color)
    LocateCentre(board, f1)
    objs.append(object('fighter', f1, [0, 0]))

    lastFireTime = None
    lastFireLaserTime = None
    lastFireMissileTime = None
    lastFireLasersTime = None
    lastEnemyTime = None
    lastEnemyRoundTime = None
    lastUFOTime = None
    lastPoint = 0
    lastLife = fighterStartLife


    info.ST = time.time()
    bgh = 0
    enemyRoundFactor = 1
    while True:

        if time.time() - info.ST < 3:
            cv2.putText(board, 'use space to shoot', (120, 400), cv2.FONT_ITALIC, 1, (105, 128, 98), 2)
        cv2.imshow('fighter', board)
        board = bg[int(bgh) % boardSize[0]: int(bgh) % boardSize[0] + boardSize[0]].copy()
        bgh -= 3

        lastPoint, lastLife = info.display(board, lastPoint, lastLife)
        if lastLife <= 0:
            cv2.putText(board, 'YOU DIE !!!', (160, 350), cv2.FONT_ITALIC, 1.5, (255, 255, 0), 2)
            file = open(src_highscore, 'r')
            hs = int(file.readline())
            if hs < info.points:
                with open(src_highscore, 'w') as f:
                    f.write(str(info.points))
            cv2.imshow('fighter', board)
            cv2.waitKey()

            main()

        key = cv2.waitKey(10)


        _ = Locate(board, objs[0].sticker, objs[0].pos)


        if key in [ord('d'), ord('D')]:
            # board = bg.copy()
            objs[0].pos[0] += fighterMoveSpeed
            flag = Locate(board, objs[0].sticker, objs[0].pos)
            if not flag:
                objs[0].pos[0] -= fighterMoveSpeed
                _ = Locate(board, objs[0].sticker, objs[0].pos)
        if key in [ord('a'), ord('A')]:
            # board = bg.copy()
            objs[0].pos[0] -= fighterMoveSpeed
            flag = Locate(board, objs[0].sticker, objs[0].pos)
            if not flag:
                objs[0].pos[0] += fighterMoveSpeed
                _ = Locate(board, objs[0].sticker, objs[0].pos)
        if key in [ord('s'), ord('S')]:
            # board = bg.copy()
            objs[0].pos[1] -= fighterMoveSpeed
            flag = Locate(board, objs[0].sticker, objs[0].pos)
            if not flag:
                objs[0].pos[1] += fighterMoveSpeed
                _ = Locate(board, objs[0].sticker, objs[0].pos)
        if key in [ord('w'), ord('W')]:
            # board = bg.copy()
            objs[0].pos[1] += fighterMoveSpeed
            flag = Locate(board, objs[0].sticker, objs[0].pos)
            if not flag:
                objs[0].pos[1] -= fighterMoveSpeed
                _ = Locate(board, objs[0].sticker, objs[0].pos)

        if info.halo is not None:
            if info.stickerbackup is None:
                info.stickerbackup = copy.deepcopy(objs[0].sticker)
                objs[0].sticker = fancy_fighter(int(fighterSize*1.1), color=info.halo['color'][:3], color_seed=info.halo['color'][-1])

            if time.time() - info.halo['ST'] > info.halo['last']:
                info.halo = None
                objs[0].sticker = copy.deepcopy(info.stickerbackup)
                info.stickerbackup = None

        if key == ord('1'):
            info.fireLevel = 1
        if key == ord('2'):
            info.fireLevel = 2
        if key == ord('3'):
            info.fireLevel = 3
        if key == ord('4'):
            info.fireLevel = 4

        # if len(a) and a[-1].name == 'space' and time.time() - a[-1].time < 0.2:
        if key == ord(' '):
            if lastFireLaserTime is None or time.time() - lastFireLaserTime > fireLaserRefill:
                fireLaser(board)
                lastFireLaserTime = time.time()

        if key in [ord('j'), ord('J')] and info.fireLevel > 0:
            if lastFireTime is None or time.time() - lastFireTime > fireRefill:
                fire(board)
                lastFireTime = time.time()

        if key in [ord('k'), ord('K')] and info.fireMissileLevel > 0:
            if lastFireMissileTime is None or time.time() - lastFireMissileTime > fireMissileRefill:
                fireMissile(board)
                lastFireMissileTime = time.time()

        if key in [ord('l'), ord('L')] and info.fireLasersLevel > 0:
            if lastFireLasersTime is None or time.time() - lastFireLasersTime > fireLasersRefill:
                fireLasers(board)
                lastFireLasersTime = time.time()
        #
        # if len(specialFighter):
        #     if specialFighter[-1] >= len(objs) or objs[specialFighter[-1]].type != 'enemy-ufo':
        #         specialFighter.remove(specialFighter[-1])


        if key in [ord('i'), ord('I')]:
            lastUFOTime = time.time()
            pos = ufoPos
            objs.append(object('enemy-ufo', boss2(), pos, hp=enemyHp['enemy-ufo']))

        if info.fireMissileLevel > 0:
            Locate(board, bullet_missile(10), (240, 200))
            bar1 = np.ones((10, 40, 3))
            bar1[:, :] = (0, 0, 0)
            if lastFireMissileTime is not None:
                if time.time() - lastFireMissileTime > fireMissileRefill:
                    bar1[:, :] = (0, 255, 0)
                else:
                    bar1[:, :int(bar1.shape[1] / fireMissileRefill * (time.time() - lastFireMissileTime))] = (0, 0, 255)
            else:
                bar1[:, :] = (0, 255, 0)
            board[575: 585, 440: 480] = bar1

        if info.fireLasersLevel > 0:
            Locate(board, laserIcon(20), (240, 170))
            bar1 = np.ones((10, 40, 3))
            bar1[:, :] = (0, 0, 0)
            if lastFireLasersTime is not None:
                if time.time() - lastFireLasersTime > fireLasersRefill:
                    bar1[:, :] = (0, 255, 0)
                else:
                    bar1[:, :int(bar1.shape[1] / fireLasersRefill * (time.time() - lastFireLasersTime))] = (0, 0, 255)
            else:
                bar1[:, :] = (0, 255, 0)
            board[615: 625, 440: 480] = bar1

        if info.fireLevel > 0:
            Locate(board, bullet(12), (240, 135))
            bar1 = np.ones((10, 40, 3))
            bar1[:, :] = (0, 0, 0)
            if lastFireTime is not None:
                if time.time() - lastFireTime > fireRefill:
                    bar1[:, :] = (0, 255, 0)
                else:
                    bar1[:, :int(bar1.shape[1] / fireRefill * (time.time() - lastFireTime))] = (0, 0, 255)
            else:
                bar1[:, :] = (0, 255, 0)
            board[655: 665, 440: 480] = bar1

        if time.time() - info.ST < game1Time:
            if lastEnemyTime is None or time.time() - lastEnemyTime > enemyShowup:
                pos = [random.randint(- boardSize[1] // 5 * 2, boardSize[1] // 5 * 2),
                       random.randint(boardSize[0] - 150, boardSize[0] - 20)]
                sticker = fancy_fighter_1(enemySize, -1)

                # while True:
                #     flag = True
                #     for i in range(len(specialFighter)):
                #         # print(len(objs))
                #         # print(specialFighter[i])
                #         if specialFighter[i] < len(objs) and objs[specialFighter[i]].type == 'enemy-ufo':
                #             obj = objs[specialFighter[i]]
                #             if is_box_intersect(get_box(pos, sticker.shape), get_box(obj.pos, obj.sticker.shape)):
                #                 pos = [random.randint(- boardSize[1] // 5 * 2, boardSize[1] // 5 * 2),
                #                        random.randint(boardSize[0] - 150, boardSize[0] - 20)]
                #                 flag = False
                #                 break
                #         else:
                #             specialFighter.remove(specialFighter[i])
                #             break
                #
                #     if flag:
                #         break

                # if ifLocate(board, fancy_fighter_1(enemySize, -1), pos):
                objs.append(object('enemy', sticker, pos, enemyHp['enemy']))
                lastEnemyTime = time.time()

            if lastEnemyRoundTime is None or time.time() - lastEnemyRoundTime > enemyShowup * 2:
                sticker = ufo(enemySize)
                # if ifLocate(board, fancy_fighter_1(enemySize, -1), pos):
                objs.append(object('enemy-round', sticker, [200 * enemyRoundFactor, 700], enemyHp['enemy-round']))
                enemyRoundFactor *= -1
                # objs.append(object('enemy-round', sticker, [200, 700], enemyHp['enemy-round']))
                lastEnemyRoundTime = time.time()

            if (time.time() - info.ST) > 5 and (lastUFOTime is None or time.time() - lastUFOTime > 15):
                info.specialfighter += 1
                lastUFOTime = time.time()
                pos = ufoPos
                objs.append(object('enemy-ufo', boss2(), pos, hp=enemyHp['enemy-ufo']))
        elif time.time() - info.ST < game1Time + 5:
            for i, obj in enumerate(objs):
                if i==0 or obj.type == 'boom':
                    continue
                else:
                    objs.append(object('boom', boom(enemySize), obj.pos))
                    objs.remove(obj)
            cv2.putText(board, 'BOOS is coming !!!', (60, 300), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
        elif time.time() - info.ST < game1Time + 6 and len(objs) <= 4:
            objs.append(object('enemy-ufo', boss2(), [0, 510], hp=enemyHp['enemy-ufo']))
            objs.append(object('enemy-ufo', boss2(), [-100, 400], hp=enemyHp['enemy-ufo']))
            objs.append(object('enemy-ufo', boss2(), [100, 400], hp=enemyHp['enemy-ufo']))
        else:
            if len(objs) == 1:
                cv2.putText(board, 'GAME 1 CLEAR!!!', (80, 300), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
                cv2.putText(board, 'SCORE:{}'.format(info.points), (80, 350), cv2.FONT_ITALIC, 1, (255, 255, 0), 2)
                file = open(src_highscore, 'r')
                hs = int(file.readline())
                if hs < info.points:
                    with open(src_highscore, 'w') as f:
                        f.write(str(info.points))
                cv2.imshow('fighter', board)
                cv2.waitKey()
                return True

        update(objs, board)

        if key == 27:
            board = np.zeros(boardSize).astype(np.uint8)
            GUI2(board)


def main():

    src = 'D:/Fighter'
    if not os.path.isdir(src):
        os.mkdir(src)

    src_highscore = os.path.join(src, 'highscore.txt')
    if not os.path.isfile(src_highscore):
        with open(src_highscore, 'w') as file:
            file.write(str(0))

    # favorite = os.path.join(src, 'favorite.txt')
    # if not os.path.isfile(favorite):
    #     with open(favorite, 'w') as file:
    #         file.write(str([2, 1, 0, 0]))

    while True:
        objs.clear()
        info.reset()
        boardSize = (800, 500, 3)
        board = np.zeros(boardSize).astype(np.uint8)

        GUI(board)
        game1(board, boardSize, src_highscore)

if __name__ == '__main__':
    main()

