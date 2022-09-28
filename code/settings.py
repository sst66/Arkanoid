
import pygame
from pygame.math import Vector2

history = [1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 3, 2, 1]
mid_index = [index for index, block in enumerate(history) if block == 1][1]
print(mid_index)
first = history[:mid_index + 1]
second = history[mid_index:]
if first == second:
    history = second
    print('repeat')
print(history)

# THIS IS A WORK IN PROGRESS
# while it is completely playable, some features are still missing
# (boss, game ending, high score tables, maybe others)

# written using VSCode with Pygame 2.1.2 (SDL 2.0.18) and Python 3.9.5

# open the 'code' folder in VSCode (not the files). 
# either right click the 'code' folder and select 'Open with Code'
# or within the VSCode File menu, select 'Open Folder' and browse
# to and select the 'code' folder 

# run 'main.py' from within VSCode or navigate your cmd window to
# the 'code' folder containing the .py files and execute 'main.py'

# This code is free and open source
# Feel free to use/edit/distribute as you see fit
# I will not be responsible for anything it does 
# to anything or anything anyone does to it
# use at your own risk

# most assets created using the latest Blender and GIMP
# some were downloaded (font, image of Ark, enemy explosion)

CHEATS = False
AUTOPLAY = False
PAUSED = False
WIDTH = 796
HEIGHT = 980
MARGIN = 32
TOPMARGIN = 100
GAP_SIZE = 2

BLOCK_MAPS = [
    # [
    # 'GGGGGGGGGGGGG',
    # '             ',
    # 'TTTDDDDDDDDDD',
    # '             ',
    # 'RRRRRRRRRRRRR',
    # '             ',
    # 'DDDDDDDDDDTTT',
    # '             ',
    # 'PPPPPPPPPPPPP',
    # '             ',
    # 'TTTDDDDDDDDDD',
    # '             ',
    # 'YYYYYYYYYYYYY',
    # '             ',
    # 'DDDDDDDDDDTTT'
    # ],
    [
    'EEEEEEEEEEEEE',
    'RRRRRRRRRRRRR',
    'YYYYYYYYYYYYY',
    'BBBBBBBBBBBBB',
    'PPPPPPPPPPPPP',
    'GGGGGGGGGGGGG'
    ], 
    [
    'W            ',
    'WO           ',
    'WOT          ',
    'WOTG         ',
    'WOTGR        ',
    'WOTGRB       ',
    'WOTGRBP      ',
    'WOTGRBPY     ',
    'WOTGRBPYW    ',
    'WOTGRBPYWO   ',
    'WOTGRBPYWOT  ',
    'WOTGRBPYWOTG ',
    'EEEEEEEEEEEER'
    ], 
    [
    'GGGGGGGGGGGGG',
    '             ',
    'TTTDDDDDDDDDD',
    '             ',
    'RRRRRRRRRRRRR',
    '             ',
    'DDDDDDDDDDTTT',
    '             ',
    'PPPPPPPPPPPPP',
    '             ',
    'TTTDDDDDDDDDD',
    '             ',
    'YYYYYYYYYYYYY',
    '             ',
    'DDDDDDDDDDTTT'
    ],
    [
    ' OTGEB YWOTG ',
    ' TGEBP WOTGE ',
    ' GEBPY OTGEB ',
    ' EBPYW TGEBP ',
    ' BPYWO GEBPY ',
    ' PYWOT EBPYW ',
    ' YWOTG BPYWO ',
    ' WOTGE PYWOT ',
    ' OTGEB YWOTG ',
    ' TGEBP WOTGE ',
    ' GEBPY OTGEB ',
    ' EBPYW TGEBP ',
    ' BPYWO GEBPY ',
    ' PYWOT EBPYW '
    ], 
    [
    '   Y     Y   ',
    '   Y     Y   ',
    '    Y   Y    ',
    '    Y   Y    ',
    '   EEEEEEE   ',
    '   EEEEEEE   ',
    '  EEREEEREE  ',
    '  EEREEEREE  ',
    ' EEEEEEEEEEE ',
    ' EEEEEEEEEEE ',
    ' EEEEEEEEEEE ',
    ' E EEEEEEE E ',
    ' E E     E E ',
    ' E E     E E ',
    '    EE EE    ',
    '    EE EE    '
    ], 
    [
    'B R G T G R B',
    'B R G T G R B',
    'B R G T G R B',
    'B R G T G R B',
    'B R G T G R B',
    'B DYDYDYDYD B',
    'B R G T G R B',
    'B R G T G R B',
    'B R G T G R B',
    'B R G T G R B',
    'Y Y D Y D Y Y',
    'B R G T G R B'
    ], 
    [
    '     YYP     ',
    '    YYPPB    ',
    '   YYPPBBR   ',
    '   YPPBBRR   ',
    '  YPPBBRRGG  ',
    '  PPBBRRGGT  ',
    '  PBBRRGGTT  ',
    '  BBRRGGTTO  ',
    '  BRRGGTTOO  ',
    '  RRGGTTOOE  ',
    '   GGTTOOE   ',
    '   GTTOOEE   ',
    '    TOOEE    ',
    '     OEE     '
    ], 

    [
    '   D D D D   ',
    ' D         D ',
    ' DD D   D DD ',
    '      D      ',
    ' D   DOD   D ',
    '   D  T  D   ',
    '      G      ',
    ' D   DBD   D ',
    '      P      ',
    ' DD D   D DD ',
    ' D         D ',
    '   D D D D   '
    ], 

    [
    ' D D     D D ',
    ' DGD     DGD ',
    ' DTD     DTD ',
    ' DDD     DDD ',
    '             ',
    '    PWWWY    ',
    '    POOOY    ',
    '    PTTTY    ',
    '    PGGGY    ',
    '    PRRRY    ',
    '    PBBBY    '
    ], 
    [
    ' D           ',
    '             ',
    ' D           ',
    ' D           ',
    ' D           ',
    ' D     B     ',
    ' D    BTB    ',
    ' D   BTWTB   ',
    ' D  BTWTWTB  ',
    ' D BTWTETWTB ',
    ' D  BTWTWTB  ',
    ' D   BTWTB    ',
    ' D    BTB    ',
    ' D     B     ',
    ' D           ',
    ' D           ',
    ' DDDDDDDDDDDD'
    ], 

    [ 
    ' EEEEEEEEEEE ',
    ' E         E ',
    ' E EEEEEEE E ',
    ' E E     E E ',
    ' E E EEE E E ',
    ' E E E E E E ',
    ' E E EEE E E ',
    ' E E     E E ',
    ' E EEEEEEE E ',
    ' E         E ',
    ' EEEEEEEEEEE '
    ], 
    [ 
    'DDDDDDDDDDDDD',
    '    D     DP ',
    ' DW D     D  ',
    ' D  D  D  D  ',
    ' D  DG D  D  ',
    ' D  D  D  D  ',
    ' D OD  D BD  ',
    ' D  D  D  D  ',
    ' D  D  D  D  ',
    ' D  D RD  D  ',
    ' D  D  D  D  ',
    ' DT    D     ',
    ' D     D    Y',
    ' DDDDDDDDDDDD'
    ], 
    [ 
    ' YYY WWW YYY ',
    ' PPP OOO PPP ',
    ' BBB TTT BBB ',
    ' RRR GGG RRR ',
    ' GGG RRR GGG ',
    ' TTT BBB TTT ',
    ' OOO PPP OOO ',
    ' WWW YYY WWW '
    ], 
    [ 
    'BBBBBBBBBBBBB',
    'D           D',
    'BBBBBBBBBBBBB',
    '             ',
    'YEEEEEEEEEEEY',
    'D           D',
    'WWWWWWWWWWWWW',
    '             ',
    'TEEEEEEEEEEET',
    'D           D',
    'RRRRRRRRRRRRR',
    '             ',
    'RRRRRRRRRRRRR',
    'D           Y'
    ], 
    [
    'TWDTTTTTTTDWT',
    'TWYDTTTTTDGWT',
    'TWYYDTTTDGGWT',
    'TWYYYDWDGGGWT',
    'TWYYYYWGGGGWT',
    'TWYYYYWGGGGWT',
    'TWYYYYWGGGGWT',
    'TEYYYYWGGGGET',
    'TTEYYYWGGGETT',
    'TTTEYYWGGETTT',
    'TTTTEYWGETTTT',
    'TTTTTEWETTTTT'
    ], 
    [ 
    '      D      ',
    '    WW WW    ',
    '  WW  D  WW  ',
    'WW  OO OO  WW',
    '  OO  D  OO  ',
    'OO  YY YY  OO',
    '  YY  D  YY  ',
    'YY  GG GG  YY',
    '  GG  D  GG  ',
    'GG  RR RR  GG',
    '  RR  D  RR  ',
    'RR  BB BB  RR',
    '  BB     BB  ',
    'BB         BB'
    ], 
    [ 
    '      E      ',
    '   BBBEGGG   ',
    '  BBBWWWGGG  ',
    '  BBWWWWWGG  ',
    ' BBBWWWWWGGG ',
    ' BBBWWWWWGGG ',
    ' BBBWWWWWGGG ',
    ' E  E E E  E ',
    '      E      ',
    '      E      ',
    '      E      ',
    '    D D      ',
    '    DDD      ',
    '     D       '
    ], 
    [ 
    'O DYYYYYYYD O',
    'O DDYYYYYDD O',
    'O D DYYYD D O',
    'O D PDYDT D O',
    'O D P E T D O',
    'O D P G T D O',
    'O D P G T D O',
    'O D P G T D O',
    'O D P G T D O',
    'ODDDP G TDDDO'
    ], 
    [ 
    '  DDDDDDDDD  ',
    '  GRPBDPBRG  ',
    '  GRPBDPBRG  ',
    '  GRPBDPBRG  ',
    '  GRPBYPBRG  ',
    '  GRPBDPBRG  ',
    '  GRPBDPBRG  ',
    '  GRPBDPBRG  ',
    '  DDDDDDDDD  '
    ], 
    [ 
    'DWDODTDGDRDBD',
    'DPDEDEDEDEDYD',
    '             ',
    'DPD D D D D D',
    'D DPD D D D D',
    'D D DPD D D D',
    'D D D DPD D D',
    'D D D D DPD D',
    '           P ',
    '  D D D DPD  ',
    '  D D DPD D  ',
    '  D DPD D D  ',
    '   PD D D    ',
    ' P    D      '
    ], 
    [ 
    ' DOOOOOOOOOD ',
    ' D         D ',
    ' D DDDDDDD D ',
    ' D D     D D ',
    ' D D     D D ',
    ' D D RRR D D ',
    ' D D GGG D D ',
    ' D D BBB D D ',
    ' D D WWW D D ',
    ' D D     D D ',
    ' D DTTTTTD D ',
    ' D         D ',
    ' D         D ',
    ' DDDDDDDDDDD '
    ], 
    [ 
    'YYYYYYYYYYYYY',
    'YYYYYYYYYYYYY',
    '             ',
    'RRD DRRRD DRR',
    'RRD DRRRD DRR',
    'RRD DRRRD DRR',
    'RRD DRRRD DRR',
    '             ',
    'WWWWWWWWWWWWW',
    'WWWWWWWWWWWWW'
    ], 
    [ 
    'TTTTTTTTTTTTT',
    '             ',
    '  EEE EEE EEE',
    '  EGE EGE EGE',
    '  EEE EEE EEE',
    '             ',
    ' EEE EEE EEE ',
    ' ERE ERE ERE ',
    ' EEE EEE EEE ',
    '             ',
    'EEE EEE EEE  ',
    'EBE EBE EBE  ',
    'EEE EEE EEE  '
    ], 
    [ 
    '     WWW     ',
    '     WWW     ',
    '     WWW     ',
    '    WWWWW    ',
    '    WBWBW    ',
    '   WBBWBBW   ',
    '   BBBBBBB   ',
    '  BBBBBBBBB  ',
    '  BBBBBBBBB  ',
    ' BBBBBBBBBBB ',
    'BBBBBBBBBBBBB'
    ], 
    [ 
    'RRRRRRRRRRRRR',
    'GGGGGGGGGGGGG',
    'BBBBBBBBBBBBB',
    'DDDDDEEEDDDDD',
    'DRRRD   DBBBD',
    'DRRRD   DBBBD',
    'D           D',
    'D           D',
    'D   DGGGD   D',
    'D   DGGGD   D',
    'DEEEDDDDDEEED'
    ], 
    [ 
    '  DEEED      ',
    ' D     D     ',
    'D  TTT  D    ',
    'D GGGGG D    ',
    'D BBBBB D    ',
    'D  PPP  D',
    ' D     D     ',
    '  DDDDD      '
    ], 
    [ 
    'EEEEEEEEEEEEE',
    'YYYYYYYYYYYYY',
    'EEEEEEEEEEEEE',
    '             ',
    'EEEEEEEEEEEEE',
    'RRRRRRRRRRRRR',
    'EEEEEEEEEEEEE'
    ], 
    [ 
    'BBBBBBBBBBBBB',
    'BDDDDPDPDDDDB',
    'BD         DB',
    'BDP       PDB',
    'BDPP     PPDB',
    'BDPPP   PPPDB',
    ' BDPPP PPPDB ',
    '  BDPPPPPDB  ',
    '   BDPPPDB   ',
    '    BDPDB    ',
    '     BPB     ',
    '      B      '
    ], 
    [ 
    'YYYYYD DYYYYY',
    'PPPPPD DPPPPP',
    'DDWDDD DDDWDD',
    'BBBBBD DBBBBB',
    'RRRRRD DRRRRR',
    'GGGGGD DGGGGG',
    'EEWEED DEEWEE',
    'TTTTTD DTTTTT',
    'OOOOOD DOOOOO',
    'WWWWWD DWWWWW'
    ], 
    [ 
    '             ',
    'YP           ',
    'YPBR         ',
    'YPBRGT       ',
    'YPBRGTOW     ',
    'YPBRGTOWYP   ',
    'EPBRGTOWYPBR ',
    ' DERGTOWYPBRG',
    '   DETOWYPBRG',
    '     DEWYPBRG',
    '       DEPBRG',
    '         DERG',
    '           DE'
    ], 
    [
    'G R B P Y W O',
    'E E E E E E E',
    ' B R G T O W ',
    ' E E E E E E ',
    'T G R B P Y W',
    'E E E E E E E',
    ' P B R G T O ',
    ' E E E E E E ',
    'O T G R B P Y',
    'E E E E E E E',
    ' Y P B R G T ',
    ' E E E E E E ',
    'W O T G R B P',
    'E E E E E E E'
    ], 
    [
    '  D D D D D  ',
    '  D D D DGG  ',
    '  D D D D D  ',
    '  D D DRRRR  ',
    '  D D D D D  ',
    '  DPPPPPPPP  ',
    '  D D D D D  ',
    '  YYYYYYYYY  ',
    '  EEEEEEEEE  '
    ], 
    [
    'EEEEEEEEEEEEE',
    'EEEEEEEEEEEEE',
    'EGGGEGGGEGGGE',
    'EGEGEGEGEEGEE',
    'EGEEEGEEEEGEE',
    'EGGGEGGGEEGEE',
    'EEEGEEEGEEGEE',
    'EGEGEGEGEEGEE',
    'EGGGEGGGEEGEE',
    'EEEEEEEEEEEEE',
    'EEEEEEEEEEEEE']]

total_blocks = 0
unkillable_blocks = 0
TOTAL_MAPS = 0
BLOCK_WIDTH = 54
BLOCK_HEIGHT = 30
#            1                 2                 3                 4 
Y_OFFSETS = [BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 2, BLOCK_HEIGHT * 3, BLOCK_HEIGHT * 4, 
#            5                 6                 7                 8 
             BLOCK_HEIGHT * 2, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, 
#            9                 10               11                 12             
             BLOCK_HEIGHT * 2, BLOCK_HEIGHT * 0, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4,
#            13               14                15                 16 
             BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 6, BLOCK_HEIGHT * 4, 
#            17                18                19                20 
             BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4,
#            21                22                23                24             
             BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 7,
#            25                26                27                28
             BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT *11, BLOCK_HEIGHT * 3,
#            29                30                31                32
             BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, BLOCK_HEIGHT * 4, 
#            33
             BLOCK_HEIGHT * 4]
# P = extra paddle, B = teleport, L = lasers, D = multiball, S = slow, C = catch, E = extend
# these will be a dic of lists of indices within each level's BLOCK_MAP to place powerups
# the keys will be index (int) and vlaues will be powerup_type (string)
# powerup_indices = [[(10, 5)], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
# types ='PFLDSGE'
powerup_dicts = [{(1, 5): 'P', (2, 5): 'B', (3, 5): 'L', (4, 5): 'D', (5, 5): 'S', (5, 5): 'C',
                  (7, 5): 'E'},  #, (6, 4): 'E', (12, 4): 'E', (8, 4): 'E', (4, 4): 'E', (2, 4): 'G',
                #  (10, 3): 'E', (6, 3): 'E', (12, 3): 'E', (8, 3): 'E', (3, 3): 'D', (2, 3): 'G'},  # 1
                {(3, 4): 'D', (1, 2): 'S'}, # 2
                {}, # 3
                {}, # 4
                {}, # 5
                {}, # 6
                {}, # 7
                {}, # 8
                {}, # 9
                {}, # 10
                {}, # 11
                {}, # 12
                {}, # 13
                {}, # 14
                {}, # 15
                {}, # 16
                {}, # 17
                {}, # 18
                {}, # 19
                {}, # 20
                {}, # 21
                {}, # 22
                {}, # 23
                {}, # 24
                {}, # 25
                {}, # 26
                {}, # 27
                {}, # 28
                {}, # 29
                {}, # 30
                {}, # 31
                {}, # 32
                {}, # 33
                ]

# vecs = [Vector2(1, .5), Vector2(1, 1), Vector2(.5, 1), 
#         Vector2(-.5, 1), Vector2(-1, 1), Vector2(-1, .5), 
#         Vector2(-1, -.5), Vector2(-1, -1), Vector2(-.5, -1), 
#         Vector2(.5, -1), Vector2(1, -1), Vector2(1, -.5)]
# new_vecs = []
# for vec in vecs:
#     new_vecs.append(vec.normalize())
# print(new_vecs)
extraball_vectors = [Vector2(0.894427, 0.447214), Vector2(0.707107, 0.707107), Vector2(0.447214, 0.894427), 
                    Vector2(-0.447214, 0.894427), Vector2(-0.707107, 0.707107), Vector2(-0.894427, 0.447214), 
                    Vector2(-0.894427, -0.447214), Vector2(-0.707107, -0.707107), Vector2(-0.447214, -0.894427), 
                    Vector2(0.447214, -0.894427), Vector2(0.707107, -0.707107), Vector2(0.894427, -0.447214)]

# extraball_vectors = [Vector2(0.258819, -0.965926), Vector2(0.707107, -0.707107),
#                 Vector2(0.965926, -0.258819), Vector2(0.965926, 0.258819),
#                 Vector2(0.707107, 0.707107), Vector2(0.258819, 0.965926),
#                 Vector2(-0.258819, 0.965926), Vector2(-0.707107, 0.707107),
#                 Vector2(-0.965926, 0.258819), Vector2(-0.965926, -0.258819),
#                 Vector2(-0.707107, -0.707107), Vector2(-0.258819, -0.965926)]




