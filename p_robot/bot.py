# bot.py -- sample balogna bot, just drops a random card

import random


def play(me, hand, rank, players, history):
    return random.choice(hand)

