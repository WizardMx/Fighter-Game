# game config
game1Time = 90

# fighter config
fighterSize = 50
fighterMoveSpeed = 20
fighterStartLife = 100

# enemy config
enemySize = 30
enemyShowup = 2
enemyMoveSpeed = {'enemy': [0, -1], 'enemy-ufo': [0, 0], 'enemy-round': [0, -1]}
enemyHp = {'enemy': 2400, 'enemy-ufo': 25000, 'enemy-round': 1500}
enemyPoints = {'enemy': 100, 'enemy-ufo': 500, 'enemy-round': 200}

ufoPos = [0, 510]

# fire config
fireSpeed = {'bullet': [0, 12], 'bulletl1': [-1, 13], 'bulletr1': [1, 13], 'bulletl2': [-2, 14], 'bulletr2': [2, 14],
             'bulletl3': [-3, 14], 'bulletr3': [3, 14],
             'bullet-laser': [0, 40], 'bullet-missile': [0, 5], 'attack-missile1': [0, -3],
             'attack-missile2': [-0.5, -3],
             'attack-missile3': [-1, -3], 'attack-missile4': [1, -3], 'attack-missile5': [0.5, -3], 'buff': [2, -1], 'buff0': [-2, -1]}

fireDamage = 800
fireSize = 10
fireRefill = 0.25

fireMissileDamage = 1200
fireMissileSize = 30
fireMissileRefill = 0.4

fireLaserDamage = 600
fireLaserSize = 100
fireLaserRefill = 0.05

fireLasersDamage = 40
fireLasersRefill = 1
# other config
boomLastTime = 0.25
