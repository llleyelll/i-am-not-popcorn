import random

map_lv1 = [ '####....',
            '......##',
            '..##....',
            '.....###',
            '...#....',
            '.....###',
            '.###....',
            '....#...',
            '.....###',
            '...#....',
            '.##.....',
            '.....###',
            '.###....',
            '.....#..',
            '###.....',
            '.....##.',
            '.###....',
            '....#...',
            '.....###',
            '...#....',
            '.##.....',
            '.....###',
            '.###....',
            '.....#..',
            '###.....',
            '.....##.',
            '.###....',
            '......##',
            '....##..',
            '###.....',
            '....###.',
            '$$$$$$$$']

map_pool = ['......##',
            '..##....',
            '.....###',
            '...#....',
            '.###....',
            '.....#..',
            '###.....',
            '.....##.',
            '....#...']

lv1_coins = [[430, 305], [520, 305],
            [300, 370], [300, 450], [300, 530],
            [300, 800], [250, 880], [180, 900],
            [650, 830], [650, 910], [650, 990],
            [100, 1105], [190, 1105], [280, 1105],
            [420, 1325], [510, 1325], [600, 1325],
            [50, 1280], [50, 1360], [50, 1440],
            [400, 1630], [490, 1630], [580, 1630],
            [300, 1730], [300, 1820], [300, 1910],
            [500, 2205], [590, 2205],
            [100, 2500], [190, 2500], [280, 2500],
            [100, 2800], [100, 2890], [100, 2980]]

def random_platform(lst):
    p = random.choice(map_pool)
    lst.append(p)