import logging

import tkinter as tk

from view import View
from model import Model


class Controller:
    def __init__(self, input_folder):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.root = tk.Tk()

        self.model = Model(input_folder)

        # register callbacks on the model observables

        self.view = View(self.root)

        # bind callbacks from user input
        self.root.bind("<KeyRelease>", self.KeyReleased)

    def run(self):
        """Start the app and run the mainloop
        """
        log = logging.getLogger(f"c.{__name__}.run")
        log.info("Running controller\n")

        self.root.mainloop()

    def KeyReleased(self, event):
        keysym = event.keysym

        if keysym == "Escape":
            self.view.exit()
        elif keysym == "F5":
            self.view.layout_cycle()
