from tkinter import Button

class ColorStyles:
        blue =      '#8685cb'
        pink =      '#c539b7'
        yellow =    '#c8c963'
        gray =      '#BBBBBB'
        red =       '#c42717'
        orange =    '#cc5500'
        black =     '#111111'


class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.brigth_span = 3

    def on_enter(self, e):
        self.newBG = '#'
        for index in range(len(self["background"])):
            if index != 0:
                hex_str = str(hex(int(self["background"][index], 16) + self.brigth_span))
                self.newBG = self.newBG + hex_str[2]
        self['background'] = self.newBG

    def on_leave(self, e):
        self.newBG = '#'
        for index in range(len(self["background"])):
            if index != 0:
                hex_str = str(hex(int(self["background"][index], 16) - self.brigth_span))
                self.newBG = self.newBG + hex_str[2]
        self['background'] = self.newBG