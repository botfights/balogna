# bullshit.py -- the bullshit botfights harness

import sys
import imp
import logging
import random
import time
import getopt

# ignore SIG_PIPE
from signal import (signal, SIGPIPE, SIG_DFL)

signal(SIGPIPE, SIG_DFL)


RANKS = 'A23456789TJQK'
RANK_ORDER = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13}


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
        num_decks = 1
        deck = []
        for i in range(num_decks) * 4:
            for rank in RANKS[:13]:
                deck.append(rank)
        random.shuffle(deck)

        # deal cards
        #
        i = 0
        cards_per_player = len(deck) // len(players_in_game)
        for player in players_in_game.values():
            player.hand = deck[i:i + cards_per_player]
            i += cards_per_player

        # set up the hand
        #
        players_in_hand = players_in_game.values()
        random.shuffle(players_in_hand)
        on_rank = 0
        whosemove = 0
        last_play_was_bullshit = False
        last_player = None
        pile = []
        history = []
        loser = None
        last_play_was_out, last_play_is_bullshit, play_is_bullshit = False, False, False
        while 1:

            # get the play from current player
            #
            p = players_in_hand[whosemove]
            players_hands = []
            for i in players_in_hand:
                players_hands.append('%s:%d' % (i.player_id, len(i.hand)))
            myhand = p.hand[:]
            myhand.sort(key = lambda x: RANK_ORDER[x])
            myhand = ''.join(myhand)
            history_str = ','.join(history)
            players_hands_str = ','.join(players_hands)
            history_str = ','.join(history)[-10:]
            logging.info('get_play("%s", "%s", "%s", "%s", "%s")' % (p.player_id, RANKS[on_rank], myhand, players_hands_str, history_str))
            play = p.get_play(p.player_id, RANKS[on_rank], myhand, players_hands_str, history_str)
            if None == play:
                play = ''
            play = str(play)[:4]
            logging.info('player %s (%s) played %s' % (p.player_id, p.playername, play))

            # is it legal? if not, just call bullshit
            #
            called_bullshit = False
            hand_counts = {}
            for i in p.hand:
                if not hand_counts.has_key(i):
                    hand_counts[i] = 0
                hand_counts[i] += 1
            play_counts = {}
            for i in play:
                if not play_counts.has_key(i):
                    play_counts[i] = 0
                play_counts[i] += 1
            last_play_is_bullshit = play_is_bullshit
            play_is_bullshit = False
            for rank, count in play_counts.items():
                if hand_counts.get(rank, 0) < count:
                    called_bullshit = True
                if rank != RANKS[on_rank]:
                    play_is_bullshit = True

            # did the last player go out? automatically call bs
            #
            if last_play_was_out:
                logging.info('last play was out, calling bullshit')
                called_bullshit = True

            # bullshit call? let's check
            #
            if called_bullshit:
                logging.info('player called bullshit')

                # take random card out of the pile
                #
                if 1 < len(pile):
                    pivot = random.randint(0, len(pile) - 1)
                    pile = pile[:pivot] + pile[pivot+1:]
                if last_play_was_bullshit:
                    logging.info('previous play was bullshit, last player takes pile')
                    last_player.hand.extend(pile)
                    pile = []
                    history.append('%s:0B' % p.player_id)
                else:
                    logging.info('previous play wasn\'t bullshit, player takes pile')
                    players_in_hand[whosemove].hand.extend(pile)
                    pile = []
                    history.append('%s:0V' % p.player_id)
                last_play_was_bullshit = False
                last_play_was_out = False

            # otherwise, take the cards out of their hand
            #
            else:

                history.append('%s:%d%s' % (p.player_id, len(i), RANKS[on_rank]))
                # remember if this is bullshit
                #
                last_player = players_in_hand[whosemove]
                last_play_was_bullshit = play_is_bullshit

                # remember if they're going out
                #
                last_play_was_out = False
                if len(play) == len(p.hand):
                    last_play_was_out = True
                for i in play:
                    pile.append(i)
                p.hand = []
                for i, j in hand_counts.items():
                    for k in range(j - play_counts.get(i, 0)):
                        p.hand.append(i)

            # advance rank
            #
            on_rank = (on_rank + 1) % 13

            # advance whosemove
            #
            last_whosemove = whosemove
            while 1:
                whosemove = (whosemove + 1) % len(players_in_hand)
                if (whosemove == last_whosemove) or (0 != len(players_in_hand[whosemove].hand)):
                    break

            # if only one player has any cards left, they lost
            #
            if whosemove == last_whosemove:
                loser = players_in_hand[whosemove]
                logging.info('end of hand, player %s (%s) lost' % (loser.player_id, loser.playername))
                break

            # nope, more players in hand, keep playing
            #
            continue

        # last player left is the loser, kick him out
        #
        del players_in_game[loser.player_id]

        # all done with hand. keep playing until there is only
        # one player
        #
        continue

    # last player left is the winner
    #
    winner = players_in_game.values()[0]
    logging.info('end of game, player %s (%s) wins' % (winner.player_id, winner.playername))
    return winner


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
bullshit -- see http://github.com/botfights/bullshit for dox

usage:

    $ python bullshit.py <command> [<option> ...] [<arg> ...]

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
