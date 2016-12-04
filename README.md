Bullshit
========

This is a game to pit [Bullshit][1] robots against each other.

Bullshit (aka Cheat, "I Doubt It") is a card game played amongst two or 
more players.

In this variation there are no wild dice, and no re-casting of dice.

You can write a robot by implementing the play() function in 
p\_robot/bot.py:

    def play(me, rank, players, history)

        me is the id of your player. eg, "A"

        rank is the rank of the next play, e.g., "2" or "J".
        at the end of a hand, all players are called with a
        rank of "Z", to let them observe game play. response
        is ignored.

        players is a list of (player_id, card_count) pairs.
        e.g.:
            
            A:2,B:10,C:4,D:0

        history is the history of plays. e.g.:

            A:2K,B:b4

        This means, player "A" called "two Kings",
        player "B" called "bullshit" but lost, and picked up
        the pile of 4 cards.

        Your function should return a list of cards to drop.

        e.g., "444" to drop three fours, or "KK4" to drop a four
        and two kings.

Your play() function will be called when it is your turn,
and at the end of the hand (in which case the most recent play
will be a call) so you can observe the showdown.

For a quick start to play against the computer:

    $ git clone https://github.com/botfights/balogna.git
    $ cd balogna
    $ python balogna.py play p_human p_computer

Next, edit p\_robot/bot.py, implement play(), then play your
robot against the computer 100 times:

    $ python balogna.py tournament --num-games=100 p_robot p_computer

Have fun!

[1]: https://en.wikipedia.org/wiki/Cheat_(game)
