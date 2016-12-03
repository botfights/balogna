# human.py -- human balogna player

import logging


def play(me, rank, hand, players, history):
    logging.info('You are player "%s" | Rank: %s | Hand: %s | Players: %s | History: %s' % (me, rank, hand, players, history))
    if 'Z' == rank:
        logging.info('Hand over. Press return to continue ...')
        raw_input()
        logging.info('*' * 50)
        return None
    logging.info('Enter move (e.g., "KK" to play two kings, or just hit enter to call balogna')
    s = raw_input()
    logging.info('*' * 50)
    return x

