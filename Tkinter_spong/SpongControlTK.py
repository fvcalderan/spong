from tkinter import Tk, Label, Button, Entry
import sys
import socket
import _thread as thread

__author__ = 'Felipe V. Calderan'
__copyright__ = 'Copyright (C) 2021 Felipe V. Calderan'
__license__ = 'BSD 3-Clause "New" or "Revised" License'
__version__ = '1.0'

class Root(Tk):
    def __init__(self):
        super().__init__()

        # Game flow variables
        self.action = None
        self.can_go = False
        self.skt    = None

        # Create widgets
        self.lblIP = Label(self, text='IP:')
        self.lblIP.pack()
        self.txtIP = Entry(self, width=20)
        self.txtIP.pack()

        self.lblPort = Label(self, text='Port:')
        self.lblPort.pack()
        self.txtPort = Entry(self, width=20)
        self.txtPort.pack()

        self.lblName = Label(self, text='Name:')
        self.lblName.pack()
        self.txtName = Entry(self, width=20)
        self.txtName.pack()

        self.lblMsg = Label(self, text='')
        self.lblMsg.pack()

        self.btnConn = Button(
            self, text='Connect', command=self.connect_tapped
        )
        self.btnConn.pack()

        self.lbl_ = Label(self, text='')
        self.lbl_.pack()

        self.btnUp = Button(
            self, text='UP', width=30, height=10, command=self.up_tapped
        )
        self.btnUp.pack()

        self.btnDown = Button(
            self, text='DOWN', width=30, height=10, command=self.down_tapped
        )
        self.btnDown.pack()


    def connect_tapped(self):
        if not self.can_go:
            self.can_go = True
            thread.start_new_thread(self.game_loop, ())
        else:
            self.error_disconnect()
            thread.start_new_thread(self.game_loop, ())


    def up_tapped(self):
        self.action = 'up'


    def down_tapped(self):
        self.action = 'down'


    def error_disconnect(self):
        self.lblMsg.configure(text='Disconnected')
        self.btnConn.configure(text='Connect')
        self.action = None
        self.can_go = False


    def game_loop(self):
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.accepted = False
        self.btnConn.configure(text='Connect')

        # Establish connection with the server
        try:
            self.skt.connect((self.txtIP.get(), int(self.txtPort.get())))
        except:
            self.error_disconnect()

        while self.can_go:
            if not self.accepted:
                # Receive host name
                try:
                    self.skt.recv(16).strip().decode()
                    self.btnConn.configure(text='Disconnect')
                except:
                    self.error_disconnect()
                    break

                # Send name
                try:
                    self.skt.send(self.txtName.get().encode().ljust(16))
                    self.accepted = True
                    self.lblMsg.configure(text='Connected')
                except:
                    self.error_disconnect()
                    break

            # Send action and receive the game status
            try:
                self.skt.send((str(self.action)).encode().ljust(16))
                self.action = None
                self.skt.recv(256)
            except:
                self.error_disconnect()
                break


if __name__ == '__main__':
    # Setup screen
    root = Root()
    root.title("SpongControl")
    root.resizable(False, False)
    root.geometry("420x600")
    root.mainloop()
