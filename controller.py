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
        log.setLevel("TRACE")
        log.info("Start init")

        self.root = tk.Tk()
        self._fullscreen_state = False

        self.model = Model()

        # register callbacks on the model observables
        self.model.output_folder.addCallback(self.changedOutputFolder)
        self.model.input_folders.addCallback(self.addedInputFolder)
        self.model.photo_info_list_active.addCallback(self.updatedPhotoList)
        self.model.current_photo_prim.addCallback(self.updatedCurrentPhotoPrim)
        self.model.selection_list.addCallback(self.updatedSelectionList)
        self.model.layout_current.addCallback(self.updatedCurrentLayout)
        self.model.cropped_prim.addCallback(self.updatedCroppedPrim)
        self.model.cropped_echo.addCallback(self.updatedCroppedEcho)

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
        # react to window resize
        self.view.frame_crop_prim.bind("<Configure>", self.frameResized)
        # scrolled *on* the image -> use e.x as rel_x, Label does *not* fill Frame
        self.view.frame_crop_prim.bind_mouse_scroll_label(self.scrolledMouseImageLabel)
        # scrolled on the frame -> consider the center as fixed
        self.view.frame_crop_prim.bind_mouse_scroll_frame(self.scrolledMouseImageFrame)

        # initialize the values in the model
        # this can't be done before, as the callback are not registered during
        # model.__init__ so the view does not update
        self.model.setOutputFolder("Not set")
        self.model.addInputFolder(input_folder)
        # set starting layout
        self.model.setLayout(1)
        self.model.setIndexPrim(0)

    def run(self):
        """Start the app and run the mainloop
        """
        log = logging.getLogger(f"c.{__class__.__name__}.run")
        log.info("Running controller\n")

        self.root.mainloop()

    def KeyReleased(self, event):
        keysym = event.keysym

        # misc
        if keysym == "Escape":
            self.view.exit()
        elif keysym == "F5":
            self.model.cycleLayout()
        elif keysym == "F11":
            self._toggle_fullscreen()

        # change photo
        elif keysym == "e":
            self.model.moveIndexPrim("forward")
        elif keysym == "q":
            self.model.moveIndexPrim("backward")
        elif keysym == "3":
            self.model.moveIndexEcho("forward")
        elif keysym == "1":
            self.model.moveIndexEcho("backward")

        # like
        elif keysym == "l" or keysym == "k":
            self.model.likePressed(keysym)

        # zoom
        if keysym == "r":
            self.model.zoomImage("in")
        if keysym == "f":
            self.model.zoomImage("out")
        if keysym == "v":
            self.model.zoomImage("reset")

        # debug
        elif keysym == "c":
            self.debug()
        elif keysym == "i":
            self.createEventMouse("up")
        elif keysym == "o":
            self.createEventMouse("down")

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

    def updatedCurrentLayout(self, lay_num):
        log = logging.getLogger(f"c.{__class__.__name__}.updatedCurrentLayout")
        log.info(f"Updated current layout")
        self.view.layout_set(lay_num)

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

    def frameResized(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.frameResized")
        #  log.setLevel("TRACE")
        log.info(f"Resized frame_crop_prim")
        widget_wid = event.widget.winfo_width()
        widget_hei = event.widget.winfo_height()
        log.trace(f"width {widget_wid} height {widget_hei}")
        self.model.doResize(widget_wid, widget_hei)

    def updatedCroppedPrim(self, data):
        log = logging.getLogger(f"c.{__class__.__name__}.updatedCroppedPrim")
        log.info(f"New value received for cropped_prim")
        self.view.frame_crop_prim.update_image(data)

    def updatedCroppedEcho(self, data):
        log = logging.getLogger(f"c.{__class__.__name__}.updatedCroppedEcho")
        log.info(f"New value received for cropped_echo")
        self.view.frame_crop_echo.update_image(data)

    def scrolledMouseImageLabel(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.scrolledMouseImageLabel")
        #  log.setLevel("TRACE")
        log.info(f"Scrolled mouse on image")
        log.trace(f"widget {event.widget} x {event.x} y {event.y}")
        log.trace(f"num {event.num} delta {event.delta}")
        if event.num == 4 or event.delta == 120 or event.delta == 1:
            direction = "in"
        elif event.num == 5 or event.delta == -120 or event.delta == -1:
            direction = "out"
        else:
            log.error(f"Unrecognized mouse event num {event.num} delta {event.delta}")
        self.model.zoomImage(direction, event.x, event.y)

    def scrolledMouseImageFrame(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.scrolledMouseImageFrame")
        #  log.setLevel("TRACE")
        log.info(f"Scrolled mouse on image frame")
        if event.num == 4 or event.delta == 120 or event.delta == 1:
            direction = "in"
        elif event.num == 5 or event.delta == -120 or event.delta == -1:
            direction = "out"
        else:
            log.error(f"Unrecognized mouse event num {event.num} delta {event.delta}")
        self.model.zoomImage(direction)

    def _toggle_fullscreen(self):
        log = logging.getLogger(f"c.{__class__.__name__}._toggle_fullscreen")
        log.setLevel("TRACE")
        self._fullscreen_state = not self._fullscreen_state
        log.trace(f"Toggling, is {self._fullscreen_state}")
        self.root.attributes("-fullscreen", self._fullscreen_state)

    def debug(self):
        log = logging.getLogger(f"c.{__class__.__name__}.debug")
        log.info(f"Useful info\n\n")  # {data}")

    def createEventMouse(self, direction):
        log = logging.getLogger(f"c.{__class__.__name__}.createEventMouse")
        log.info(f"Creating FakeEvent mouse {direction}")
        fe = FakeEvent()
        if direction == "up":
            fe.num = 4
        else:
            fe.num = 5
        fe.x = 270
        fe.y = 200
        fe.widget = None
        fe.delta = 0
        self.scrolledMouseImageLabel(fe)


class FakeEvent(tk.Event):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
