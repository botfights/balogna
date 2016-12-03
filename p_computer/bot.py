# computer.py -- sample balogna bot

import random
import logging

def play(me, hands, history):

    # figure out the previous call
    #
    if 0 == len(history):
        prev_quantity, prev_face = 0, 0
    else:
        x = int(history.split(',')[-1].split(':')[1])
        prev_quantity, prev_face = x // 10, x % 10

    # showdown? if so, just ignore
    #
    if 0 == prev_quantity and len(history) > 0:
        return 0

    # count the total number of dice
    #
    num_dice = sum(map(lambda x : len(x.split(':')[1]),hands.split(',')))

    # find my hand
    #
    my_hand = None
    for i in hands.split(','):
        who, dice = i.split(':')

        if who == me:
            my_hand = dice
            if len(history) == 0:
                return '1' + my_hand[0]

            break

    # try 4 times to find pick
    # a random better play, if
    # can't, just call
    #
    for i in range(4):

        # pick a random face from my dice
        #
        face = int(my_hand[random.randint(0,len(my_hand) - 1)])

        # pick a random quantity, skew it low
        #
        quantity = 1 + int(abs(random.normalvariate(0.0,num_dice / 6.0)))

        # is it a bigger call than the previous?
        #
        if (quantity > prev_quantity) or ((quantity == prev_quantity) and (face > prev_face)) :

            # if so, return it
            #
            return (quantity * 10) + face

    # nothing found, just call
    #
    logging.debug('nothing found, calling ...')
    return 0

