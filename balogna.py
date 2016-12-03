# balogna.py -- the balogna test harness

HELP = '''\
usage:

    To play a game against the computer:

        $ python balogna.py play p_human p_computer

    To play a 10 game tourney between p_robot and p_computer and p_dummy:

        $ python balogna.py tournament 10 p_robot p_human p_dummy
'''

import sys
import imp
import logging
import random
import time

# ignore SIG_PIPE
from signal import (signal,
                    SIGPIPE,
                    SIG_DFL)

signal(SIGPIPE, SIG_DFL)


import random,logging,sys

def verbose_play(play) :
    if 0 :
        pass
    elif 0 == play :
        return 'LIAR!'
    elif 1 == (play // 10) :
        return 'one %s' % STR_NUM_SINGULAR.get(play % 10,'???')
    else :
        return '%s %s' % (STR_NUM_SINGULAR.get(play // 10,'%d' % (play // 10)),STR_NUM_PLURAL.get(play % 10,'???'))

def get_play(game_id,hand_num,who,f_get_play,player_name,hands_str,history_str,catch_exceptions) :
    play = 0
    try :
        play = int(f_get_play(who,hands_str,history_str))
    except KeyboardInterrupt :
        raise
    except :
        if not catch_exceptions :
            raise
        logging.warn('caught exception "%s" calling %s (%s) \'s get_play() function' % (sys.exc_info()[1],who,player_name))
    logging.debug('LOG_PLAY\tG%sH%d\t%s-%s\t%s\t%s\t%d' % (game_id,hand_num,who,player_name,hands_str,history_str,play))
    return play

def play_game(game_id,players,player_names,catch_exceptions) :
    
    # first, set up the players left in the game
    #
    seats = players.keys()
    seats.sort()
    random.shuffle(seats)
    whose_move = 0
    cups = {}
    dice = RULES_DICE
    faces = RULES_FACES
    for i in seats :
        cups[i] = dice

    logging.info('=' * 50)
    logging.info('new game between %s' % ', '.join(map(lambda x : '%s-%s' % (x,player_names[x]),seats)))

    # keep playing hands until only one player left
    #
    hand_num = 0
    while 1 :
        hand_num += 1

        # only one player left?
        #
        winner = None
        for i in seats :
            if 0 != cups[i] :
                if None != winner :
                    winner = None
                    break
                winner = i
        if None != winner :
            break

        # everyone rolls their dice
        #
        logging.info('-' * 50)
        logging.info('new hand between %s with %s dice, respectfully' % (', '.join(map(lambda x : '%s-%s' % (x,player_names[x]),filter(lambda x : 0 != cups[x],seats))),', '.join(map(lambda x : '%d' % cups[x],filter(lambda x : 0 != cups[x],seats)))))
        hands = {}
        for i in seats :
            if 0 == cups[i] :
                continue
            hands[i] = []
            logging.debug('rolling %d dice for %s ...' % (cups[i],i))
            for j in range(cups[i]) :
                hands[i].append(random.randint(1,faces))
            hands[i].sort(reverse=True)

        logging.debug('hands: %s' % str(filter(lambda x : 0 != cups[x[0]],hands.items())))
        
        # keep playing hands until someone calls liar
        #
        history = []
        while 1 :
            
            logging.debug('getting move from %s ...' % seats[whose_move])

            # build history
            #
            history_str = ','.join(map(lambda x : '%s:%d' % (seats[x[0]],x[1]),history))

            # build hands
            #
            hands_str = None
            for i in seats :
                if None == hands_str :
                    hands_str = ''
                else :
                    hands_str += ','
                if i == seats[whose_move] :
                    hands_str += '%s:%s' % (seats[whose_move],''.join(map(lambda x : str(x),hands[seats[whose_move]])))
                else :
                    hands_str += '%s:%s' % (i,'x' * cups[i])

            # get the play
            #
            play = get_play(game_id,hand_num,seats[whose_move],players[seats[whose_move]],player_names[seats[whose_move]],hands_str,history_str,catch_exceptions)
            logging.info('player %s calls "%s"' % (seats[whose_move],verbose_play(play)))

            # check for legal moves
            # 
            if 0 != play :
                face = play % 10
                quantity = play // 10
                if face <= 0 or face > faces or quantity <= 0 or quantity > (len(players) * dice) :
                    logging.info('illegal move, assuming calling liar')
                    play = 0
                elif 0 != len(history) :
                    last_play = history[-1][1]
                    last_face = last_play % 10
                    last_quantity = last_play // 10
                    if (quantity < last_quantity) or ((quantity == last_quantity) and (face <= last_face)) :
                        logging.info('not increasing play, assuming calling liar')
                        play = 0

            # remember the play
            #
            history.append((whose_move,play))
            
            # if it's a call, or an illegal move, or a bet less than the last play
            # treat it as a call and check the bluff
            #
            loser = None
            result = None
            if 0 == play :
                
                # if it's the first play, they lose
                #
                if 1 == len(history) :
                    logging.debug('called liar before any plays')
                    loser = seats[whose_move]
                    result = 1

                else :
                    
                    # count dice
                    #
                    common_dice = {}
                    for i in seats :
                        if 0 == cups[i] :
                            continue
                        for j in hands[i] :
                            common_dice[j] = common_dice.get(j,0) + 1
 
                    last_play = history[-2][1]
                    last_face = last_play % 10
                    last_quantity = last_play // 10
 
                    logging.debug('hands: %s' % str(hands))
                    logging.debug('common dice: %s' % str(common_dice))

                    logging.info('player %s-%s calls liar on player %s-%s\'s call of %s' % (seats[whose_move],player_names[seats[whose_move]],seats[history[-2][0]],player_names[seats[history[-2][0]]],verbose_play(last_play)))
                    logging.info('hands: %s' % ', '.join(map(lambda x : '%s:%s' % (x,''.join(map(lambda y : str(y),hands[x]))),filter(lambda x : 0 != cups[x],seats))))
                    logging.info('common dice: %s' % ', '.join(map(lambda x : verbose_play((x[1] * 10) + x[0]),common_dice.items())))

                    if common_dice.get(last_face,0) >= last_quantity :
                        logging.debug('%s\'s last play was %d %d\'s, CORRECT, %s loses' % (seats[history[-2][0]],last_quantity,last_face,seats[whose_move]))
                        loser = seats[whose_move]
                        result = 2
                    else :
                        logging.debug('%s\'s last play was %d %d\'s, INCORRECT, %s loses' % (seats[history[-2][0]],last_quantity,last_face,seats[history[-2][0]]))
                        loser = seats[history[-2][0]]
                        result = 3

                # remove loser's die, bump them if they're out of dice,
                # and start over again
                #
                # show everyone the result
                #
                logging.debug('showing everyone the result')
                history_str = ','.join(map(lambda x : '%s:%d' % (seats[x[0]],x[1]),history))
                hands_str = ','.join(map(lambda x : '%s:%s' % (x,''.join(map(lambda y : str(y),hands[x]))),filter(lambda x : 0 != cups[x],seats)))
                logging.debug('LOG_HAND\tG%sH%d\t%s\t%s\tLOSER:%s-%s\t%d' % (game_id,hand_num,hands_str,history_str,loser,player_names[loser],result))
                logging.info('player %s-%s loses one die' % (loser,player_names[loser]))
                cups[loser] -= 1
                if 0 == cups[loser] :
                    logging.info('player %s-%s has no dice left' % (loser,player_names[loser]))
                for i in seats :
                    get_play(game_id,hand_num,i,players[i],player_names[i],hands_str,history_str,catch_exceptions)
              
            # advance next move
            #
            while 1 :
                whose_move += 1
                if whose_move == len(seats) :
                    whose_move = 0
                if 0 != cups[seats[whose_move]] :
                    break

            # new hand if necessary
            #
            if None != loser :
                break

    logging.debug('LOG_GAME\t%s\t%s' % (game_id,winner))
    logging.info('player %s-%s wins' % (winner,player_names[winner]))
    return winner

def play_games(n, seed, playernames, catch_exceptions):
    random.seed(seed)
    logging.debug('SEED\t%s' % seed)
    players = {}
    scores = {}
    names = {}
    for i in playernames:
        playername, path, modulename, attr = split_playername(i)
        logging.info('playername: %s => %s' % (i, split_playername(i)))
        player_id = chr(ord('A') + len(players))
        names[player_id] = playername
        logging.info('making player %s (%s) ...' % (player_id, playername))
        p = make_player(playername, path, modulename, attr, catch_exceptions)
        players[player_id] = p
        scores[player_id] = 0
    game_num = 0
    for r in range(n):
        game_num += 1
        logging.debug('playing game %d ...' % (game_num, ))
        winner = liarsdice.play_game(game_num, players, names, catch_exceptions)
        scores[winner] += 1
        logging.debug('RESULT\tgame:%d\twinner:%s' % (game_num, winner))
        k = scores.keys()
        k.sort(key = lambda x: scores[x], reverse = True)
        rank = 0
        for i in k:
            rank += 1
            logging.info('SCORE\tgame %d of %d\t#%d.\t%s\t%s\t%d' % (game_num, n, rank, i, names[i], scores[i]))
        logging.info('SCORE')
        logging.info('STATUS\t%.2f\t\t%s' % (game_num/float(n), ','.join(map(lambda i : '%s:%s' % (names[i], scores[i]), k))))
    return scores


def play_tournament(t, n, players):
    scores = {}
    for i in range(len(players)):
        scores[i] = 0
    for r in range(t) :
        for i in range(len(players)):
            for j in range(len(players)):
                if i >= j:
                    continue
                x = play_game(n, players[i], players[j])
                if 0 == x :
                    scores[i] += 1
                else :
                    scores[j] += 1
                logging.info('SCORE\t%d\t%d\t%d\t%d\t%d\t%d\t%s\t%s' % (r,t,i,j,scores[i],scores[j],players[i].playername,players[j].playername))
        logging.info('BOTFIGHTS\t%d\t%d\t%s' % (r, t,'\t'.join(map(lambda i : '%s:%s' % (players[i].playername,scores[i]),range(len(players))))))
    logging.info('BOTFIGHTS\t%d\t%d\t%s' % (t, t,'\t'.join(map(lambda i : '%s:%s' % (players[i].playername,scores[i]),range(len(players))))))
    return -1


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
    p.get_play = lambda x, y, z: call_player(p, (x, y, z), random.choice((1, 2, 3)))
    return p


def usage():
    print('''\
liars dice -- see http://github.com/botfights/liarsdice for dox

usage:

    $ python liarsdice.py <command> [<option> ...] [<arg> ...]

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


def main(argv):
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
        player1 = make_player('a', args[0])
        player2 = make_player('b', args[1])
        winner = play_game(race_to, player1, player2)
        sys.exit()

    elif 'tournament' == command:
        logging.basicConfig(level=log_level, format='%(message)s', 
                        stream=sys.stdout)
        players = []
        for player_id, playername in enumerate(args):
            players.append(make_player(chr(ord('a') + player_id), playername))
        play_tournament(num_games, race_to, players)
        sys.exit()

    else:
        print 'i don\'t know how to "%s".' % command
        usage()
        sys.exit()


if __name__ == '__main__':
    main(sys.argv[1:])
