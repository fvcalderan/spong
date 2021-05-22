"""This script is meant to be ran in Pythonista 3, alongside its UI script"""

import ui
import sys
import socket
from objc_util import ObjCInstance, on_main_thread

__author__ = 'Felipe V. Calderan'
__copyright__ = 'Copyright (C) 2021 Felipe V. Calderan'
__license__ = 'BSD 3-Clause "New" or "Revised" License'
__version__ = '1.0'

# Game flow variables
action = None
can_go = False
skt    = None


@on_main_thread
def set_kb_apperance(txt_box):
    '@type txt_box: ui.TextBox'
    # set keyboard appearance to dark
    if isinstance(txt_box, ui.TextView):
        ObjCInstance(tv).setKeyboardAppearance_(1)
    elif isinstance(txt_box, ui.TextField):
        ObjCInstance(txt_box).subviews()[0].setKeyboardAppearance_(1)
    else:
        raise TypeError('Expected TextBox-like ui element')


def connect_tapped(sender):
    '@type sender: ui.Button'
    global can_go
    if not can_go:
        can_go = True
        game_loop(sender.superview)
    else:
        error_disconnect(sender.superview)
        game_loop(sender.superview)


def up_tapped(sender):
    '@type sender: ui.Button'
    global action
    action = 'up'


def down_tapped(sender):
    '@type sender: ui.Button'
    global action
    action = 'down'


def error_disconnect(v):
    '@type v: ui.View'
    global skt
    v['lblMsg'].text_color = 'red'
    v['lblMsg'].text = 'Disconnected'
    v['btnConn'].title = 'Connect'
    action = None
    can_go = False
    skt.close()


@ui.in_background
def game_loop(v):
    '@type v: ui.View'
    global action, can_go, skt

    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    accepted = False
    v['btnConn'].title = 'Connect'

    # Establish connection with the server
    try:
        skt.connect((v['txtIP'].text, int(v['txtPort'].text)))
    except:
        error_disconnect(v)

    while can_go:
        if not accepted:
            # Receive host name
            try:
                skt.recv(16).strip().decode()
                v['btnConn'].title = 'Disconnect'
            except:
                error_disconnect(v)
                break

            # Send name
            try:
                skt.send(v['txtName'].text.encode().ljust(16))
                accepted = True
                v['lblMsg'].text_color = 'lightgreen'
                v['lblMsg'].text = 'Connected'
            except:
                error_disconnect(v)
                break

        # Send action and receive the game status
        try:
            skt.send(str(action).encode().ljust(16))
            action = None
            skt.recv(256)
        except:
            error_disconnect(v)
            break


if __name__ == '__main__':
    v = ui.load_view()

    # Keyboard in dark mode
    set_kb_apperance(v['txtIP'])
    set_kb_apperance(v['txtPort'])
    set_kb_apperance(v['txtName'])

    # present in fullscreen in dark mode
    v.present('fullscreen', title_bar_color='black', title_color='white')
