#! /bin/python3

import sys
import socket
import curses
import pickle
from random import choice

try:
    from AI import AI
    AI_AVAILABLE = True
except:
    AI_AVAILABLE = False

__author__ = 'Felipe V. Calderan'
__copyright__ = 'Copyright (C) 2021 Felipe V. Calderan'
__license__ = 'BSD 3-Clause "New" or "Revised" License'
__version__ = '1.0'

# Arena config variables
SCR_H = 18
SCR_W = 78

# Message variables
MSG_SCR_SMALL = 'Terminal screen is too small (80x20 required)'
MSG_ARG_WRONG = 'Usage: python3 spong.py host/join ip port player_name'
MSG_CANT_HOST = 'Could not open the server on this IP/port'
MSG_CANT_JOIN = 'Could not join the game on this IP/port'
MSG_WAITING   = 'Waiting for another player... (Ctrl+C to cancel)'
MSG_DISCONN   = '----------Disconnected----------'


class Arena:
    """Used to draw and store informations about the arena"""

    def __init__(
        self,
        x : int,
        y : int,
        size_x : int,
        size_y : int
    ):
        """Initialize arena with the top-left corner located at (x,y) and with
        size (size_x, size_y)"""
        self.x,       self.y       = x, y
        self.size_x,  self.size_y  = size_x, size_y
        self.bound_x, self.bound_y = x+size_x, y+size_y


    def draw(self, screen : curses.window):
        """Draws the arena on the screen"""
        for i in range(self.y, self.bound_y):
            screen.addstr(i, self.x, '|')
            screen.addstr(i, self.bound_x, '|')

        for i in range(self.x, self.bound_x):
            screen.addstr(self.y, i, '-')
            screen.addstr(self.bound_y, i, '-')

        screen.addstr(self.y,       self.x,       '+')
        screen.addstr(self.bound_y, self.x,       '+')
        screen.addstr(self.y,       self.bound_x, '+')
        screen.addstr(self.bound_y, self.bound_x, '+')


class Player:
    """Deals with players position, score and drawing"""

    def __init__(self, side : str, arena : Arena):
        """Define player position based on if it's player 1 or player 2"""
        self.x     = arena.x+2 if side == 'left' else arena.bound_x-2
        self.y     = arena.bound_y//2+arena.y//2
        self.score = 0


    def goal(self):
        """Player scored a point"""
        self.score += 1


    def move(self, direction : str):
        """Move player up or down"""
        if direction == 'up': self.y -= 1
        else                : self.y += 1


    def draw(self, screen : curses.window, arena : Arena):
        """Draw player on the screen's defined y position"""
        # clear player's row
        for i in range(arena.y+1, arena.bound_y-1):
            screen.addstr(i, self.x, ' ')

        # draw the player
        screen.addstr(self.y-1, self.x, '|')
        screen.addstr(self.y,   self.x, '|')
        screen.addstr(self.y+1, self.x, '|')


class Ball:
    """Deals with balls's collisions, goals, position and velocity"""

    def __init__(self, x : int, y : int, vx : int, vy : int):
        """Define ball position and initial velocity"""
        self.old_x, self.old_y = x, y
        self.x,     self.y     = x, y
        self.vx,    self.vy    = vx, vy


    def move(self, player1 : Player, player2 : Player, arena : Arena) -> int:
        """Move ball given its pos, velocity, collision and check for goals"""
        goal = 0

        # Check for map borders
        if self.y + self.vy > arena.bound_y-1 or self.y + self.vy < arena.y+1:
            self.vy *= -1

        if self.x == arena.x+1 or self.x == arena.bound_x-1:
            if self.x == arena.bound_x-1: player1.goal()
            else                        : player2.goal()
            self.old_x, self.old_y = self.x, self.y
            self.x = arena.bound_x//2+arena.x//2
            self.y = arena.bound_y//2+arena.y//2
            self.vx, self.vy = choice((-1, 1)), choice((-1, 0, 1))
            return

        # Check for player hit
        if self.x == player1.x+1:
            if   self.y == player1.y  : self.vx, self.vy = (1, 0)
            elif self.y == player1.y-1: self.vx, self.vy = (1,-1)
            elif self.y == player1.y+1: self.vx, self.vy = (1, 1)
            elif self.y == player1.y-2 and self.vy == 1: self.vx,self.vy=(1,-1)
            elif self.y == player1.y+2 and self.vy ==-1: self.vx,self.vy=(1, 1)

        if self.x == player2.x-1:
            if   self.y == player2.y  : self.vx, self.vy = (-1,  0)
            elif self.y == player2.y-1: self.vx, self.vy = (-1, -1)
            elif self.y == player2.y+1: self.vx, self.vy = (-1,  1)
            elif self.y == player2.y-2 and self.vy== 1: self.vx,self.vy=(-1,-1)
            elif self.y == player2.y+2 and self.vy==-1: self.vx,self.vy=(-1, 1)

        # Set the new ball position (and old position)
        self.old_x, self.old_y = self.x, self.y
        self.x,     self.y     = self.x + self.vx, self.y + self.vy


    def draw(self, screen : curses.window):
        """(Re)draw the ball"""
        # Erase the ball from the old position
        screen.addstr(self.old_y, self.old_x, ' ')

        # Draw the ball on the new position
        screen.addstr(self.y, self.x, 'O')


    def upload(self) -> (int, int, int, int):
        """Returns only the essential informations about the ball, so that the
        whole object doesn't need to be passed through the network

        Returns
        -------

        stats : tuple(int, int, int, int)
            quadruple with ball's x, y, vx and vy

        """
        return (self.x, self.y, self.vx, self.vy)

    def download(self, info : tuple):
        """Update the essential informations about the ball"""
        self.x, self.y, self.vx, self.vy = info


def show_msg(
    screen        : curses.window,
    screen_height : int,
    screen_width  : int,
    message       : str
):
    """Generic routine to generate an error message"""
    screen.addstr(screen_height//2, screen_width//2-len(message)//2, message)
    screen.nodelay(0)
    screen.getch()
    sys.exit(0)


def get_args(
    screen        : curses.window,
    screen_height : int,
    screen_width  : int
) -> (str, str, int, str):
    """Verify if the arguments are correctly formatted, if they are, return
    them type-casted and further formatted for convenience

    Returns
    -------

    tuple(mode : str, ip : str, port : int, name : str)
    """
    # Wrong number of arguments
    if len(sys.argv) != 5:
        show_msg(screen, screen_height, screen_width, MSG_ARG_WRONG)

    # Invalid mode (only host/join permitted)
    if sys.argv[1].lower() not in ('host', 'join'):
        show_msg(screen, screen_height, screen_width, MSG_ARG_WRONG)

    # Invalid port type
    if not sys.argv[3].isdigit():
        show_msg(screen, screen_height, screen_width, MSG_ARG_WRONG)

    return sys.argv[1].lower(), sys.argv[2], int(sys.argv[3]), sys.argv[4][:16]


def get_action(
    screen      : curses.window,
    arena       : Arena,
    player      : Player,
    keys        : dict,
    is_AI       : bool,
    game_status : dict
) -> str or None:
    """Get player's action. The purpuse of this function is to be a wrapper,
    for convenience if one day another kind of control is to be implemented

    Parameters
    ----------

    screen      : curses.window
    arena       : Arena
    player      : Player
    keys        : dict
        dictionary containing all the configured key to play the game
    is_AI       : bool
        if True, the AI will control the character (if an AI is available)
    game_status : dict
        dictionary containing players y position and ball position & velocity.
        Useful to create an AI, for exemple.

    Returns
    -------

    action : str
        string containing what the player wants to do
    action : None
        if no action (or invalid action) is taken
    """
    if is_AI and AI_AVAILABLE:
        return AI(screen, arena, player, keys, is_AI, game_status)
    else:
        key = screen.getch()

        if key in keys['up_key']     : return 'up'
        elif key in keys['down_key'] : return 'down'
        elif key in keys['quit_key'] : return 'quit'

        return None


def main(scr : curses.window):
    # Remove blinking cursor
    curses.curs_set(0)

    # Get screen's height and width & check if the screen is big enough
    sh, sw = scr.getmaxyx()
    if sh < SCR_H+2 or sw < SCR_W+2: show_msg(scr, sh, sw, MSG_SCR_SMALL)

    # Get args
    mode, ip, port, plname = get_args(scr, sh, sw)

    # Start socket for host/join mode
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if mode == 'host':
        try:
            skt.bind((ip, port))
            skt.listen(1)
        except:
            show_msg(scr, sh, sw, MSG_CANT_HOST)
    else:
        try:
            skt.connect((ip, port))
        except:
            show_msg(scr, sh, sw, MSG_CANT_JOIN)

    # Setup keys
    up_key    = set((curses.KEY_UP,   ord('k'), ord('K'), ord('w'), ord('W')))
    down_key  = set((curses.KEY_DOWN, ord('j'), ord('J'), ord('s'), ord('S')))
    quit_key  = set((ord('q'), ord('Q')))
    keys = {'up_key' : up_key, 'down_key' : down_key, 'quit_key' : quit_key}

    # Activate nodelay (so getch won't interrupt the execution)
    scr.nodelay(1)
    scr.timeout(33)

    # Create arena
    arena = Arena(0, 1, SCR_W, SCR_H)

    # Create players
    player1 = Player('left', arena)
    player2 = Player('right', arena)

    # Create the ball
    ball = Ball(
        arena.bound_x//2, arena.bound_y//2, choice((-1, 1)), choice((-1, 0, 1))
    )

    # Connection accepted
    accepted = False

    # Waiting connection message
    scr.addstr(sh//2, sw//2-len(MSG_WAITING)//2, MSG_WAITING)
    scr.refresh()
    scr.addstr(sh//2, 0, " "*sw)

    # Draw the arena
    arena.draw(scr)

    # Game loop
    while True:
        # Start networking
        if mode == 'host':
            if not accepted:
                # Accept client
                try:
                    clskt, claddr = skt.accept()
                except:
                    sys.exit()
                # Write host name on the screen and send it
                scr.addstr(0, 0, plname)
                clskt.send(plname.encode().ljust(16))
                # Receive client name and add to screen
                try:
                    clname = clskt.recv(16).strip().decode()[:16]
                except:
                    show_msg(scr, 0, SCR_W, MSG_DISCONN)
                scr.addstr(0, SCR_W+1-len(clname), clname)
                # Mark client as accpeted
                accepted = True
        else:
            if not accepted:
                # Receive host name and add to screen
                try:
                    scr.addstr(0, 0, skt.recv(16).strip().decode()[:16])
                except:
                    show_msg(scr, 0, SCR_W, MSG_DISCONN)
                # Write client name on the screen and send it
                scr.addstr(0, SCR_W+1-len(plname), plname)
                skt.send(plname.encode().ljust(16))
                accepted = True

        # Draw the game score
        scr.addstr(0, SCR_W//2-6, str(player1.score))
        scr.addstr(0, SCR_W//2+6, str(player2.score))

        # Draw players
        player1.draw(scr, arena)
        player2.draw(scr, arena)

        # Draw ball (host) and check goals
        if mode == 'host':
            ball.move(player1, player2, arena)
            ball.draw(scr)

        # Get button press, perform action and send over the network
        if mode == 'host':
            action = get_action(
                scr, arena, player1, keys, plname=='AI',
                {**{'p1' : player1.y, 'p2' : player2.y},
                 **{'ball' : ball.upload()}}
            )
            if action == 'up' and player1.y > arena.y+3:
                player1.move('up')
            elif action == 'down' and player1.y < arena.bound_y-3:
                player1.move('down')
            elif action == 'quit' :
                clskt.close()
                sys.exit(0)
            else: action = None

            # Send ball and host's action
            try:
                clskt.send(pickle.dumps((str(action), ball.upload())))
                player2_action = clskt.recv(16).strip().decode()
                if player2_action == 'up' and player2.y > arena.y+3:
                    player2.move('up')
                elif player2_action == 'down' and player2.y < arena.bound_y-3:
                    player2.move('down')
            except:
                show_msg(scr, 0, SCR_W, MSG_DISCONN)

        else:
            action = get_action(
                scr, arena, player2, keys, plname=='AI',
                {**{'p1' : player1.y, 'p2' : player2.y},
                 **{'ball': ball.upload()}}
            )
            if action == 'up' and player2.y > arena.y+3 :
                player2.move('up')
            elif action == 'down' and player2.y < arena.bound_y-3:
                player2.move('down')
            elif action == 'quit':
                skt.close()
                sys.exit(0)
            else: action = None

            # Send client's action, then get ball and host's position
            try:
                skt.send(str(action).encode().ljust(16))
                player1_action, ball_info = pickle.loads(
                    skt.recv(sys.getsizeof(('down', ball.upload()))*3)
                )
                if player1_action == 'up' and player1.y > arena.y+3:
                    player1.move('up')
                elif player1_action == 'down' and player1.y < arena.bound_y-3:
                    player1.move('down')
                ball.download(ball_info)
            except:
                show_msg(scr, 0, SCR_W, MSG_DISCONN)

            # Draw ball (join) and check goals
            ball.move(player1, player2, arena)
            ball.draw(scr)

        scr.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
