# Square  方片    =>  sq  =>  RGB蓝色(Blue)
# Plum    梅花    =>  pl  =>  RGB绿色(Green)
# Spade   黑桃    =>  sp  =>  RGB黑色(Black)
# Heart   红桃    =>  he  =>  RGB红色(Red)

init_poker = {
    'local': {
        'head': [None, None, None],
        'mid': [None, None, None, None, None],
        'tail': [None, None, None, None, None],
        'drop': [None, None, None, None]
    },
    'player1': {
        'head': [None, None, None],
        'mid': [None, None, None, None, None],
        'tail': [None, None, None, None, None],
        'drop': [None, None, None, None]
    },
    'player2': {
            'head': [None, None, None],
            'mid': [None, None, None, None, None],
            'tail': [None, None, None, None, None],
            'drop': [None, None, None, None]
        }
}

# Square
Blue = {
    '2': 0,
    '3': 1,
    '4': 2,
    '5': 3,
    '6': 4,
    '7': 5,
    '8': 6,
    '9': 7,
    '10': 8,
    'J': 9,
    'Q': 10,
    'K': 11,
    'A': 12
}

# Plum
Green = {
    '2': 13,
    '3': 14,
    '4': 15,
    '5': 16,
    '6': 17,
    '7': 18,
    '8': 19,
    '9': 20,
    '10': 21,
    'J': 22,
    'Q': 23,
    'K': 24,
    'A': 25
}

# Heart
Red = {
    '2': 26,
    '3': 27,
    '4': 28,
    '5': 29,
    '6': 30,
    '7': 31,
    '8': 32,
    '9': 33,
    '10': 34,
    'J': 35,
    'Q': 36,
    'K': 37,
    'A': 38
}

# Spade
Black = {
    '2': 39,
    '3': 40,
    '4': 41,
    '5': 42,
    '6': 43,
    '7': 44,
    '8': 45,
    '9': 46,
    '10': 47,
    'J': 48,
    'Q': 49,
    'K': 50,
    'A': 51
}

POKER_SCOPE = [
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    'J',
    'Q',
    'K',
    'A'
]
