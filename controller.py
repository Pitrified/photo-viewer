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
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        self.root = tk.Tk()

        self.model = Model()

        # register callbacks on the model observables
        self.model.output_folder.addCallback(self.changedOutputFolder)
        self.model.input_folders.addCallback(self.addedInputFolder)
        self.model.photo_info_list_active.addCallback(self.updatedPhotoList)
        self.model.current_photo_prim.addCallback(self.updatedCurrentPhotoPrim)
        self.model.selection_list.addCallback(self.updatedSelectionList)

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
        # react to input folder toggling
        self.view.frame_path_info.input_frame.bind(
            "<<toggle_input_folder>>", self.toggledInputFolder
        )
        # react to doubleclick on a ThumbButton
        self.view.frame_path_info.photo_list_frame.bind(
            "<<thumbbtn_photo_doubleclick>>", self.doubleclikedThumbbtnPhoto
        )
        self.view.frame_path_info.photo_list_frame.bind(
            "<<thumbbtn_selection_doubleclick>>", self.doubleclikedThumbbtnSelection
        )

        # initialize the values in the model
        # this can't be done before, as the callback are not registered during
        # model.__init__ so the view does not update
        self.model.setOutputFolder("Not set")
        self.model.addInputFolder(input_folder)
        self.model.setIndexPrim(0)

    def run(self):
        """Start the app and run the mainloop
        """
        log = logging.getLogger(f"c.{__class__.__name__}.run")
        log.info("Running controller\n")

        self.root.mainloop()

    def KeyReleased(self, event):
        keysym = event.keysym

        if keysym == "Escape":
            self.view.exit()
        elif keysym == "F5":
            self.view.layout_cycle()

        elif keysym == "e":
            self.model.moveIndexPrim("forward")
        elif keysym == "q":
            self.model.moveIndexPrim("backward")
        elif keysym == "3":
            self.model.moveIndexEcho("forward")
        elif keysym == "1":
            self.model.moveIndexEcho("backward")

        elif keysym == "l" or keysym == "k":
            if self.view.layout_current in self.view.layout_is_double:
                self.model.likePressed(keysym)
            else:
                # if the layout is not double send the event from prim
                self.model.likePressed("k")

        elif keysym == "c":
            self.debug()

    def setOutputFolder(self):
        log = logging.getLogger(f"c.{__class__.__name__}.setOutputFolder")
        #  log.setLevel("TRACE")
        log.info(f"Obtain new value")

        output_folder_full = tk.filedialog.askdirectory()
        log.trace(
            f"Value received '{output_folder_full}' type {type(output_folder_full)}"
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
        log = logging.getLogger(f"c.{__class__.__name__}.changedOutputFolder")
        log.info(f"New value '{data}'")
        self.view.frame_path_info.update_output_frame(data)

    def addInputFolder(self):
        log = logging.getLogger(f"c.{__class__.__name__}.addInputFolder")
        #  log.setLevel("TRACE")
        log.info(f"Add an input folder")

        input_folder_full = tk.filedialog.askdirectory()
        log.trace(
            f"Value received '{input_folder_full}' type {type(input_folder_full)}"
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
        log = logging.getLogger(f"c.{__class__.__name__}.addedInputFolder")
        log.info(f"New values received for input_folders")  # {data}")
        self.view.frame_path_info.update_input_frame(data)

    def toggledInputFolder(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.toggledinputfolder")
        log.info(f"toggled input folder")

        state = self.view.frame_path_info.checkbtn_input_state
        self.model.toggleInputFolder(state)

    def updatedPhotoList(self, data):
        log = logging.getLogger(f"c.{__class__.__name__}.updatedPhotoList")
        log.info(f"New values received for photo_info_list_active")  # {data}")
        self.view.frame_path_info.update_photo_list(data)

    def updatedCurrentPhotoPrim(self, data):
        log = logging.getLogger(f"c.{__class__.__name__}.updatedCurrentPhotoPrim")
        log.info(f"New value received for current_photo_prim {data}")
        self.view.frame_path_info.update_current_photo_prim(data)

    def updatedSelectionList(self, data):
        log = logging.getLogger(f"c.{__class__.__name__}.updatedSelectionList")
        log.info(f"New values received for selection_list")  # {data}")
        self.view.frame_path_info.update_selection_list(data)

    def doubleclikedThumbbtnPhoto(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.doubleclikedThumbbtnPhoto")
        #  log.setLevel("TRACE")
        log.info(f"doublecliked Thumbbtn photo")
        pic = self.view.frame_path_info.photo_doubleclicked
        log.trace(f"On pic {pic}")
        self.model.seekIndexPrim(pic)

    def doubleclikedThumbbtnSelection(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.doubleclikedThumbbtnPhoto")
        log.setLevel("TRACE")
        log.info(f"doublecliked Thumbbtn selection")
        pic = self.view.frame_path_info.selection_doubleclicked
        log.trace(f"On pic {pic}")
        self.model.toggleSelectionPic(pic)

    def debug(self):
        log = logging.getLogger(f"c.{__class__.__name__}.debug")
        log.info(f"Useful info\n\n")  # {data}")
