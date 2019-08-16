import logging

import tkinter as tk

class LabelPixel(tk.Frame):
    """label with width set in pixel

    http://code.activestate.com/recipes/578887-text-widget-width-and-height-in-pixels-tkinter/
    https://stackoverflow.com/questions/14887610/specify-the-dimensions-of-a-tkinter-text-box-in-pixels
    """

    def __init__(self, parent, width=0, height=0, **kwargs):
        self.width = width
        self.height = height

        # create external frame of specified dimensions
        tk.Frame.__init__(self, parent, width=self.width, height=self.height)

        # create internal label
        self.label_widget = tk.Label(self, **kwargs)

        # make the label grow in the entire frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.label_widget.grid(row=0, column=0, sticky="nsew")

    def pack(self, *args, **kwargs):
        tk.Frame.pack(self, *args, **kwargs)
        self.pack_propagate(False)

    def grid(self, *args, **kwargs):
        tk.Frame.grid(self, *args, **kwargs)
        self.grid_propagate(False)

    def config(self, *args, **kwargs):
        self.label_widget.config(*args, **kwargs)

    def bind(self, *args, **kwargs):
        self.label_widget.bind(*args, **kwargs)



