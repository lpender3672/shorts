import tkinter as tk
from PIL import Image, ImageTk


class display(object):

    def __init__(self, dim, factor, fullscreen = False, anchor = "nw"):


        self.f = factor


        self.w = dim[0]
        self.h = dim[1]

        self.fullscreen = fullscreen

