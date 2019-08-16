from tkinter import filedialog
import tkinter as tk
import logging

from os import makedirs
from os.path import isdir

from view import View
from model import Model
from utils import format_color


class Controller:
    def __init__(self, input_folder):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.root = tk.Tk()

        self.model = Model()

        # register callbacks on the model observables
        self.model.output_folder.addCallback(self.changedOutputFolder)
        self.model.input_folders.addCallback(self.addedInputFolder)

        self.view = View(self.root)

        # bind callbacks from user input
        # general keypress
        self.root.bind("<KeyRelease>", self.KeyReleased)
        # button to set new output_folder
        self.view.frame_path_info.btn_set_output_folder.config(
            command=self.setOutputFolder
        )
        # button to add another input_folder
        self.view.frame_path_info.btn_add_folder.config(command=self.addInputFolder)

        # initialize the values in the model
        # this can't be done before, as the callback are not registered during
        # model.__init__ so the view does not update
        self.model.setOutputFolder("Not set")
        self.model.addInputFolder(input_folder)

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

    def setOutputFolder(self):
        log = logging.getLogger(f"c.{__name__}.setOutputFolder")
        #  log.setLevel("TRACE")
        log.info(f"Obtain new value")

        output_folder_full = tk.filedialog.askdirectory()
        log.log(
            5, f"Value received '{output_folder_full}' type {type(output_folder_full)}"
        )

        # filedialog sometimes returns an empty tuple, sometimes an empty string
        # if isinstance(output_folder_full, tuple) or output_folder_full == '':
        if len(output_folder_full) == 0:
            log.info(f"Selection of output_folder cancelled")
            return

        log.info(
            f'{format_color("Output", "spring green")} folder: {output_folder_full}'
        )

        # create the folder if it doesn't exist
        if not isdir(output_folder_full):
            log.warn(f"Not a folder '{output_folder_full}', creating it")
            makedirs(output_folder_full)

        self.model.setOutputFolder(output_folder_full)

    def changedOutputFolder(self, data):
        log = logging.getLogger(f"c.{__name__}.changedOutputFolder")
        log.info(f"New value '{data}'")
        self.view.frame_path_info.update_output_frame(data)

    def addInputFolder(self):
        log = logging.getLogger(f"c.{__name__}.addInputFolder")
        #  log.setLevel("TRACE")
        log.info(f"Add an input folder")

        input_folder_full = tk.filedialog.askdirectory()
        log.log(
            5, f"Value received '{input_folder_full}' type {type(input_folder_full)}"
        )

        # filedialog sometimes returns an empty tuple, sometimes an empty string
        if len(input_folder_full) == 0:
            log.info(f"Selection of input_folder cancelled")
            return

        if not isdir(input_folder_full):
            log.error(f"Not a valid folder: {input_folder_full}")

        log.info(f'{format_color("Input", "spring green")} folder: {input_folder_full}')

        self.model.addInputFolder(input_folder_full)

    def addedInputFolder(self, data):
        log = logging.getLogger(f"c.{__name__}.addedInputFolder")
        log.info(f"New values received")# {data}")
        self.view.frame_path_info.update_input_frame(data)

