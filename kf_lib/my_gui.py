#! python3

import tkinter as tk

from . import game


# fg = foreground (e.g. text on buttons)
# bg = background

#    Frame, Label, Entry, Text, Canvas, Button, Radiobutton,
#    Checkbutton, Scale, Listbox, Scrollbar, OptionMenu, Spinbox
#    LabelFrame and PanedWindow


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.master.title('Kung-fu World')
        self.g = game.Game()
        self.create_widgets()

    def create_widgets(self):
##        self.canv = tk.Canvas(self)
##        self.canv.pack()

        self.lbl = tk.Label(self, text='Press one of the buttons below.',
                                                            width=100, height=30)
        self.lbl.pack()

        self.ng_button = tk.Button(self, text='New Game', command=self.new_game)
        self.ng_button.pack()

        self.lg_button = tk.Button(self, text='Load Game',
                                                        command=self.load_game)
        self.lg_button.pack()


##        self.QUIT = tk.Button(self, text="QUIT", fg="red", command=root.destroy)
##        self.QUIT.pack(side='right')
##
##        self.make_button = tk.Button(self, text='Make Summaries',
##                                                        command=self.make_sum)
##        self.make_button.pack(side='right')
##
##        self.test_button = tk.Button(self, text='TEST', command=self.test)
##        self.test_button.pack(side='right')

    def load_game(self):
        self.g.load_game('save.txt')
        self.destroy()
        self.g.play()

    def new_game(self):
        self.g.new_game()
        self.destroy()
        self.g.play()


root = tk.Tk()
app = Application(master=root)
app.mainloop()