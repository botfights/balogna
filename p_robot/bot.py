# bot.py -- sample balogna bot, just drops a random card

import random


def play(me, rank, hand, players, history):
    return random.choice(hand)

