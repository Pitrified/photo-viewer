import logging

from tkinter import filedialog  # noqa: F401
import tkinter as tk

from model import Model
from utils import format_color
from view import View


class Controller:
    def __init__(self, input_folder):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info("Start init")

        self.root = tk.Tk()
        self.root.winfo_toplevel().title("Photo Viewer")
        self._fullscreen_state = False

        self.model = Model()

        # register callbacks on the model observables
        self.model.output_folder.addCallback(self.updatedOutputFolder)
        self.model.input_folders.addCallback(self.updatedInputFolder)
        self.model.photo_info_list_active.addCallback(self.updatedPhotoList)
        self.model.current_photo_prim.addCallback(self.updatedCurrentPhotoPrim)
        self.model.selection_list.addCallback(self.updatedSelectionList)
        self.model.layout_current.addCallback(self.updatedCurrentLayout)
        self.model.cropped_prim.addCallback(self.updatedCroppedPrim)
        self.model.cropped_echo.addCallback(self.updatedCroppedEcho)
        self.model.metadata_prim.addCallback(self.updatedMetadataPrim)
        self.model.metadata_echo.addCallback(self.updatedMetadataEcho)

        self.view = View(self.root)

        # bind callbacks from user input
        # general keypress
        self.root.bind("<KeyRelease>", self.KeyReleased)

        # button to set new output_folder
        self.view.frame_path_info.output_frame.btn_set_output_folder.config(
            command=self.setOutputFolder
        )
        # button to save selection
        self.view.frame_path_info.output_frame.btn_save_selection.config(
            command=self.saveSelection
        )

        # button to add another input_folder
        self.view.frame_path_info.input_frame.btn_add_folder.config(
            command=self.addInputFolder
        )
        # react to input folder toggling
        self.view.frame_path_info.input_frame.bind(
            "<<toggle_input_folder>>", self.toggledInputFolder
        )

        # react to doubleclick on a ThumbButton
        self.view.frame_path_info.photo_list_frame.bind(
            "<<thumbbtn_photo_doubleclick>>", self.doubleclikedThumbbtnPhoto
        )
        self.view.frame_path_info.selection_list_frame.bind(
            "<<thumbbtn_selection_doubleclick>>", self.doubleclikedThumbbtnSelection
        )

        # react to window resize
        self.view.frame_crop_prim.bind("<Configure>", self.frameResized)

        # scrolled *on* the image -> use e.x as rel_x, Label does *not* fill Frame
        self.view.frame_crop_prim.bind_mouse_scroll_label(self.scrolledMouseImageLabel)
        self.view.frame_crop_echo.bind_mouse_scroll_label(self.scrolledMouseImageLabel)
        # scrolled on the frame -> consider the center as fixed
        self.view.frame_crop_prim.bind_mouse_scroll_frame(self.scrolledMouseImageFrame)
        self.view.frame_crop_echo.bind_mouse_scroll_frame(self.scrolledMouseImageFrame)

        # clicked on image
        self.view.frame_crop_prim.bind_image("<Button-1>", self.clickedImage)
        self.view.frame_crop_echo.bind_image("<Button-1>", self.clickedImage)
        # moved mouse
        self.view.frame_crop_prim.bind_image("<B1-Motion>", self.movedImageMouse)
        self.view.frame_crop_echo.bind_image("<B1-Motion>", self.movedImageMouse)

        # some trickery is needed to distinguish single and doubleClick
        # https://stackoverflow.com/a/50622349/2237151
        # right click -> index prim forward
        self.view.frame_crop_prim.bind_to_all(
            "<Button-3>", self.rightClickedFrameCropPrim
        )
        # right double click -> index prim backward
        #  self.view.frame_crop_prim.bind_to_all(
        #  "<Double-Button-3>", self.rightDoubleClickedFrameCropPrim
        #  )
        self._right_double_click_frame_crop_prim = False
        # left double click -> save current image

        # initialize the values in the model
        # this can't be done before, as the callback are not registered during
        # model.__init__ so the view does not update
        self.model.addInputFolder(input_folder)
        # set starting layout
        self.model.setLayout(2)
        self.model.setIndexPrim(0)

    def run(self):
        """Start the app and run the mainloop"""
        logg = logging.getLogger(f"c.{__class__.__name__}.run")
        logg.info("Running controller\n")

        self.root.mainloop()

    def KeyReleased(self, event):
        """Bind Key to functions

        Using the numpad is hard: https://stackoverflow.com/q/45869902/2237151
        """
        keysym = event.keysym

        # misc
        if keysym == "Escape":
            self.view.exit()
        elif keysym == "F4":
            self.model.swapDoubleLayout()
        elif keysym == "F5":
            self.model.cycleLayout()
        elif keysym == "F11":
            self._toggle_fullscreen()

        # change photo
        elif keysym == "e" or keysym == "KP_2":
            self.model.moveIndexPrim("forward")
        elif keysym == "q" or keysym == "KP_1":
            self.model.moveIndexPrim("backward")
        elif keysym == "3" or keysym == "KP_5":
            self.model.moveIndexEcho("forward")
        elif keysym == "1" or keysym == "KP_4":
            self.model.moveIndexEcho("backward")
        elif keysym == "2" or keysym == "KP_0":
            self.model.moveIndexEcho("sync")

        # like
        elif keysym == "k" or keysym == "KP_3":
            self.model.likePressed("prim")
        elif keysym == "l" or keysym == "KP_6":
            self.model.likePressed("echo")

        # move photo
        if keysym == "d":
            self.model.moveImageDirection("right")
        if keysym == "a":
            self.model.moveImageDirection("left")
        if keysym == "w":
            self.model.moveImageDirection("up")
        if keysym == "s":
            self.model.moveImageDirection("down")

        # zoom
        if keysym == "r":
            self.model.zoomImage("in")
        if keysym == "f":
            self.model.zoomImage("out")
        if keysym == "x":
            self.model.zoomImage("reset")

        # debug
        elif keysym == "c":
            self.debug()
        elif keysym == "i":
            self.createEventMouse("up")
        elif keysym == "o":
            self.createEventMouse("down")

    def setOutputFolder(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.setOutputFolder")
        #  logg.setLevel("TRACE")
        logg.info("Obtain new value")

        output_folder_full = tk.filedialog.askdirectory()
        logg.trace(
            f"Value received '{output_folder_full}' type {type(output_folder_full)}"
        )

        # filedialog sometimes returns an empty tuple, sometimes an empty string
        # if isinstance(output_folder_full, tuple) or output_folder_full == '':
        if len(output_folder_full) == 0:
            logg.info("Selection of output_folder cancelled")
            return

        logg.info(
            f'{format_color("Output", "spring green")} folder: {output_folder_full}'
        )

        self.model.setOutputFolder(output_folder_full)

    def updatedOutputFolder(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedOutputFolder")
        logg.info(f"New value '{data}'")
        self.view.frame_path_info.output_frame.update_output_frame(data)

    def saveSelection(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.saveSelection")
        #  logg.setLevel("TRACE")
        logg.info("Saving selected pics")
        self.model.saveSelection()

    def addInputFolder(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.addInputFolder")
        #  logg.setLevel("TRACE")
        logg.info("Add an input folder")

        input_folder_full = tk.filedialog.askdirectory()
        logg.trace(
            f"Value received '{input_folder_full}' type {type(input_folder_full)}"
        )

        # filedialog sometimes returns an empty tuple, sometimes an empty string
        if len(input_folder_full) == 0:
            logg.info("Selection of input_folder cancelled")
            return

        logg.info(
            f'{format_color("Input", "spring green")} folder: {input_folder_full}'
        )

        self.model.addInputFolder(input_folder_full)

    def updatedInputFolder(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedInputFolder")
        logg.info("New values received for input_folders")  # {data}")
        self.view.frame_path_info.input_frame.update_input_frame(data)

    def toggledInputFolder(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.toggledinputfolder")
        logg.info("Toggled input folder")
        state = self.view.frame_path_info.input_frame.checkbtn_input_state
        self.model.toggleInputFolder(state)

    def updatedCurrentLayout(self, lay_num):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedCurrentLayout")
        logg.info("Updated current layout")
        self.view.layout_set(lay_num)

    def updatedPhotoList(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedPhotoList")
        logg.info("New values received for photo_info_list_active")  # {data}")
        self.view.frame_path_info.photo_list_frame.update_photo_list(data)

    def updatedCurrentPhotoPrim(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedCurrentPhotoPrim")
        logg.info("New value received for current_photo_prim")
        self.view.frame_path_info.photo_list_frame.update_current_photo_prim(data)

    def updatedSelectionList(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedSelectionList")
        logg.info("New values received for selection_list")  # {data}")
        self.view.frame_path_info.selection_list_frame.update_selection_list(data)

    def doubleclikedThumbbtnPhoto(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.doubleclikedThumbbtnPhoto")
        #  logg.setLevel("TRACE")
        logg.info("Doublecliked Thumbbtn photo")
        pic = self.view.frame_path_info.photo_list_frame.photo_doubleclicked
        logg.trace(f"On pic {pic}")
        self.model.seekIndexPrim(pic)

    def doubleclikedThumbbtnSelection(self, event):
        logg = logging.getLogger(
            f"c.{__class__.__name__}.doubleclikedThumbbtnSelection"
        )
        #  logg.setLevel("TRACE")
        logg.info("Doublecliked Thumbbtn selection")
        pic = self.view.frame_path_info.selection_list_frame.selection_doubleclicked
        logg.trace(f"On pic {pic}")
        self.model.toggleSelectionPic(pic)

    def frameResized(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.frameResized")
        #  logg.setLevel("TRACE")
        logg.info("Resized frame_crop_prim")
        widget_wid = event.widget.winfo_width()
        widget_hei = event.widget.winfo_height()
        logg.trace(f"width {widget_wid} height {widget_hei}")
        self.model.doResize(widget_wid, widget_hei)

    def updatedCroppedPrim(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedCroppedPrim")
        #  logg.setLevel("TRACE")
        logg.trace("New value received for cropped_prim")
        self.view.frame_crop_prim.update_image(data)

    def updatedCroppedEcho(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedCroppedEcho")
        #  logg.setLevel("TRACE")
        logg.trace("New value received for cropped_echo")
        self.view.frame_crop_echo.update_image(data)

    def updatedMetadataPrim(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedMetadataPrim")
        #  logg.setLevel("TRACE")
        logg.info("New value received for metadata_prim")
        self.view.frame_metadata.update_meta_prim(data)

    def updatedMetadataEcho(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updatedMetadataEcho")
        #  logg.setLevel("TRACE")
        logg.info("New value received for metadata_echo")
        self.view.frame_metadata.update_meta_echo(data)

    def scrolledMouseImageLabel(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.scrolledMouseImageLabel")
        #  logg.setLevel("TRACE")
        logg.info("Scrolled mouse on image")
        logg.trace(f"widget {event.widget} x {event.x} y {event.y}")
        logg.trace(f"num {event.num} delta {event.delta}")
        if event.num == 4 or event.delta == 120 or event.delta == 1:
            direction = "in"
        elif event.num == 5 or event.delta == -120 or event.delta == -1:
            direction = "out"
        else:
            logg.error(f"Unrecognized mouse event num {event.num} delta {event.delta}")
        self.model.zoomImage(direction, event.x, event.y)

    def scrolledMouseImageFrame(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.scrolledMouseImageFrame")
        #  logg.setLevel("TRACE")
        logg.info("Scrolled mouse on image frame")
        if event.num == 4 or event.delta == 120 or event.delta == 1:
            direction = "in"
        elif event.num == 5 or event.delta == -120 or event.delta == -1:
            direction = "out"
        else:
            logg.error(f"Unrecognized mouse event num {event.num} delta {event.delta}")
        self.model.zoomImage(direction)

    def clickedImage(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.clickedImage")
        #  logg.setLevel("TRACE")
        logg.info("Clicked mouse on image")
        self.model.saveMousePos(event.x, event.y)

    def movedImageMouse(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.movedImageMouse")
        #  logg.setLevel("TRACE")
        logg.trace("Moved mouse on image")
        self.model.moveImageMouse(event.x, event.y)

    def rightClickedFrameCropPrim(self, event):
        """Setup delayed callback for eventual doubleclick"""
        logg = logging.getLogger(f"c.{__class__.__name__}.rightClickedFrameCropPrim")
        #  logg.setLevel("TRACE")
        logg.trace("Callback for right click")
        # this works but I hate it, it is too slow to react
        #  event.widget.after(200, self.rightClickActionFrameCropPrim, event)
        self.rightClickActionFrameCropPrim(event)

    def rightDoubleClickedFrameCropPrim(self, event):
        """Set flag that a doubleclick happened"""
        logg = logging.getLogger(
            f"c.{__class__.__name__}.rightDoubleClickedFrameCropPrim"
        )
        #  logg.setLevel("TRACE")
        logg.trace("Callback for right doubleclick")
        self._right_double_click_frame_crop_prim = True

    def rightClickActionFrameCropPrim(self, event):
        """Actual action for Click or DoubleClick"""
        logg = logging.getLogger(
            f"c.{__class__.__name__}.rightClickActionFrameCropPrim"
        )
        #  logg.setLevel("TRACE")
        logg.trace("Action for right doubleclick or click")

        if self._right_double_click_frame_crop_prim:
            self._right_double_click_frame_crop_prim = False
            logg.trace("Double click!")
            self.model.moveIndexPrim("backward")
        else:
            logg.trace("Single click!")
            self.model.moveIndexPrim("forward")

    def _toggle_fullscreen(self):
        logg = logging.getLogger(f"c.{__class__.__name__}._toggle_fullscreen")
        #  logg.setLevel("TRACE")
        self._fullscreen_state = not self._fullscreen_state
        logg.trace(f"Toggling, is {self._fullscreen_state}")
        self.root.attributes("-fullscreen", self._fullscreen_state)

    def debug(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.debug")
        logg.info("Useful info\n\n")  # {data}")

    def createEventMouse(self, direction):
        logg = logging.getLogger(f"c.{__class__.__name__}.createEventMouse")
        logg.info(f"Creating FakeEvent mouse {direction}")
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
