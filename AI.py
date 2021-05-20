import curses
from random import choice
import time

__author__ = 'Felipe V. Calderan'
__copyright__ = 'Copyright (C) 2021 Felipe V. Calderan'
__license__ = 'BSD 3-Clause "New" or "Revised" License'
__version__ = '1.0'

# Random variable for the AI
RND = 0

# AI Atrociousness : int (from 4 to 60. The higher, the more atrocious)
ATROCIOUSNESS = 10 # A.K.A "difficulty level"

def AI(screen, arena, player, keys, is_AI, game_status) -> str or None:
    """An AI will send the inputs to the game"""

    time.sleep(0.033)

    global ATROCIOUSNESS
    global RND

    if ATROCIOUSNESS < 4: ATROCIOUSNESS = 4
    if ATROCIOUSNESS > 60: ATROCIOUSNESS = 60

    if ATROCIOUSNESS+2 > abs(game_status['ball'][0]-player.x) > ATROCIOUSNESS:
        RND = choice((-1, 0, 1))

    elif ATROCIOUSNESS > abs(game_status['ball'][0]-player.x) > 1:
        if game_status['ball'][3] != 0:
            if   game_status['ball'][1] < player.y : return 'up'
            elif game_status['ball'][1] > player.y : return 'down'
            else                                   : return None

        else:
            if   game_status['ball'][1] < player.y + RND : return 'up'
            elif game_status['ball'][1] > player.y + RND : return 'down'
            else                                         : return None
