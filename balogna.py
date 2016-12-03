# balogna.py -- the balogna botfights harness

import sys
import imp
import logging
import random
import time
import getopt

# ignore SIG_PIPE
from signal import (signal, SIGPIPE, SIG_DFL)

signal(SIGPIPE, SIG_DFL)


class Player:
    pass


def play_game(players):
    for i in players:
        x = i.get_play(1, '234K', 3, 4, 5)
        logging.info('%s played %s' % (i.player_id, str(x)))
    return random.choice(players)


def play_tournament(games, players):
    for i in players:
        i.score = 0
    for gamenum in range(games):
        x = play_game(players)
        x.score += 1
        logging.info('BOTFIGHTS\t%d\t%d\t%s' % (gamenum, games, '\t'.join(map(lambda i : '%s:%s' % (i.playername, i.score), players))))
    return None


class Player():
    pass


def call_player(player, args, default):
    global g_catch_exceptions
    result = default
    start = time.clock()
    try:
        result = player.play(*args)
    except KeyboardInterrupt:
        raise
    except:
        logging.warn('caught exception "%s" calling %s (%s)'
                     % (sys.exc_info()[1], player.player_id, player.playername))
        if not g_catch_exceptions:
            raise
    elapsed = time.clock() - start
    player.elapsed += elapsed
    player.calls += 1
    return result


def make_player(player_id, dirname):
    global g_catch_exceptions
    m = None
    try:
        name = 'bot'
        (f, filename, data) = imp.find_module(name, [dirname, ])
        m = imp.load_module(name, f, filename, data)
    except:
        logging.error('caught exception "%s" loading %s' % \
                      (sys.exc_info()[1], dirname))
        if not g_catch_exceptions:
            raise
    p = Player()
    p.player_id = player_id
    p.playername = dirname
    z = p.playername.rfind('/')
    if -1 != z:
        p.playername = p.playername[z + 1:]
    p.play = None
    if None == m or not hasattr(m, 'play'):
        logging.error('%s has no function "play"; ignoring ...' % dirname)
    else:
        p.play = getattr(m, 'play')
    p.elapsed = 0.0
    p.calls = 0
    p.get_play = lambda v, w, x, y, z: call_player(p, (v, w, x, y, z), None)
    return p


def usage():
    print('''\
balogna -- see http://github.com/botfights/balogna for dox

usage:

    $ python balogna.py <command> [<option> ...] [<arg> ...]

commands:

    game [<player1>] [<player2>] ...

                        play a single game between players

    tournament [<player1>] [<player2>] ...

                        play a tournament between players
options:

    -h, --help                      show this help
    --seed=<s>                      set seed for random number generator
    --catch-exceptions=<off|on>     catch and log exceptions
    --num-games=<n>                 set number of games for tournament (defaults to 100)

    --log-level=<n>                 set log level (10 debug, 20 info, 40 error)
''')


if __name__ == '__main__':
    argv = sys.argv[1:]
    if 1 > len(argv):
        usage()
        sys.exit()
    command = argv[0]
    try:
        opts, args = getopt.getopt(argv[1:], "h", [
                                                    "help",
                                                    "seed=",
                                                    "catch-exceptions=",
                                                    "num-games=",
                                                    "log-level=",
                                                    ])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(1)
    seed = time.time()
    num_games = 100
    log_level = logging.DEBUG
    global g_catch_exceptions
    g_catch_exceptions = False
    for o, a in opts:
        if 0:
            pass
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("--seed", ):
            seed = a
        elif o in ("--num-games", ):
            num_games = int(a)
        elif o in ("--log-level", ):
            log_level = int(a)
        elif o in ("--catch-exceptions", ):
            g_catch_exceptions = 'off' != a
        else:
            raise Exception("unhandled option")
    random.seed(seed)

    if 0:
        pass

    elif 'game' == command:
        logging.basicConfig(level=log_level, format='%(message)s',
                        stream=sys.stdout)
        players = []
        for i in args:
            players.append(make_player(chr(ord('A') + len(players)), i))
        winner = play_game(players)
        sys.exit()

    elif 'tournament' == command:
        logging.basicConfig(level=log_level, format='%(message)s', 
                        stream=sys.stdout)
        players = []
        for i in args:
            players.append(make_player(chr(ord('a') + len(players)), i))
        play_tournament(num_games, players)
        sys.exit()

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()
