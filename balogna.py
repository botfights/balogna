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


RANKS = '23456789TJQKA'


def play_game(players):

    # to start, everyone is in the game
    #
    players_in_game = {}
    for i in players:
        players_in_game[i.player_id] = i

    # keep playing until there's only 1 player left
    #
    while 1 < len(players_in_game):

        # build and shuffle the decks
        #
        num_decks = (len(players_in_game) // 4) + 1
        deck = []
        for i in range(num_decks) * 4:
            for rank in RANKS:
                deck.append(rank)
        random.shuffle(deck)

        # deal cards
        #
        i = 0
        cards_per_player = len(deck) // len(players_in_game)
        for player in players_in_game.values():
            player.hand = deck[i:i + cards_per_player]
            player.hand.sort()
            i += cards_per_player

        # keep playing until one player left
        #
        players_in_hand = players_in_game.values()
        random.shuffle(players_in_hand)

        # start at '2'
        #
        on_rank = 0
        whosemove = 0
        last_play_was_bullshit = False
        last_player = None
        pile = []
        history = ''
        while 1:

            # get the play from current player
            #
            players_hands = []
            for i in players_in_hand:
                players_hands.append((i.player_id, len(i.hand)))
            print str(players_hands)
            p = players_in_hand[whosemove]
            play = p.get_play(p.player_id, RANKS[on_rank], p.hand, players_hands, history)
            if None == play:
                play = ''
            play = str(play)

            # is it legal? if not, just call bullshit
            #
            played_bullshit = False
            hand_counts = {}
            for i in players[whosemove].hand:
                if not hand_counts.has_key(i):
                    hand_counts[i] = 0
                hand_counts[i] += 1
            play_counts = {}
            for i in play:
                if not play_counts.has_key(i):
                    play_counts[i] = 0
                play_counts[i] += 1
            play_is_bullshit = False
            for rank, count in play_counts.items():
                if hand_counts.get(rank, 0) < count:
                    played_bullshit = True
                if rank != on_rank:
                    play_is_bullshit = True

            # bullshit call? let's check
            #
            if played_bullshit:
                logging.info('player called bullshit')
                if last_play_was_bullshit:
                    logging.info('previous play was bullshit, plast player takes pile')
                    last_player.hand.extend(pile)
                    pile = []
                else:
                    logging.info('previous play wasn\'t bullshit, player takes pile')
                    players[whosemove].hand.extend(pile)
                    pile = []
                last_play_was_bullshit = False

            # otherwise, take the cards out of their hand
            #
            else:

                # remember if this is bullshit
                #
                last_player = players[whosemove]
                last_play_was_bullshit = play_is_bullshit
                for i in play:
                    pile.append(i)

            # advance rank
            #
            on_rank = (on_rank + 1) % 13

            # advance whosemove
            last_whosemove = whosemove
            while 1:
                whosemove = (whosemove + 1) % len(players_in_hand)
                if 0 != len(players[whosemove].hand):
                    break

            # if only one player has any cards left, they lost
            #
            if whosemove == last_whosemove:
                logging.info('end of hand, player %s lost' % players[whosemove].playername)
                break

            # nope, more players in hand, keep playing
            #
            continue

        # last player left is the loser, kick him out
        #
        loser = players_in_hand[0]
        del players_in_game[loser.player_id]

        # all done with hand. keep playing until there is only
        # one player
        #
        continue

    # last player left is the winner
    #
    logging.info('end of game, player %s wins' % players_in_game.values()[0])
    return players_in_game.values()[0]


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
