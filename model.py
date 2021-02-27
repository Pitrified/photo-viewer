from fractions import Fraction
from math import ceil
from math import log
from math import sqrt
from os import listdir
from os import makedirs
from os.path import basename
from os.path import isdir
from os.path import join
from os.path import splitext
from shutil import copy2
from sys import getsizeof
import logging

from PIL import Image  # type: ignore
from PIL import ImageTk

from observable import Observable
from photo_info import PhotoInfo
from utils import format_color


class Model:
    def __init__(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info("Start init")

        self._out_fold_not_set = "Not set not known"
        self.output_folder = Observable(self._out_fold_not_set)
        self.input_folders = Observable({})

        # dict to send photo_info -> only active photos
        self.photo_info_list_active = Observable({})
        # remember all PhotoInfo loaded
        self._photo_info_list_all = {}
        # dict to send (selection_info, status) -> keep in de-selected one
        self.selection_list = Observable({})

        # full path of the current_photo_prim
        self.current_photo_prim = Observable("")
        # index in self._active_photo_list of current photo
        self._index_prim = 0
        # full path of the current_photo_echo
        self.current_photo_echo = Observable("")
        self._index_echo = 0

        # set of valid photo extensions to load in _active_photo_list
        self._is_photo_ext = set((".jpg", ".jpeg", ".JPG", ".png"))
        # thumbnail size for ThumbButtons
        self._thumb_size = 50
        # how much to move the image from keyboard
        self._mov_delta = 200

        # ImageTk that holds the cropped picture
        self.cropped_prim = Observable(None)
        self.cropped_echo = Observable(None)
        # cache dimension for the Holder
        self._cropper_cache_dim = 10
        self._loaded_croppers = Holder(self._cropper_cache_dim)
        self._widget_wid = -1
        self._widget_hei = -1

        # dict of metadata {name:value}
        self.metadata_prim = Observable({})
        self.metadata_echo = Observable(None)
        self._load_named_metadata()

        # setup layout info
        self._layout_tot = 6
        self._layout_is_double = (1, 5)
        self.layout_current = Observable(0)
        self._old_single_layout = 0
        # double layout to jump to when swapDoubleLayout is called
        self._basic_double_layout = 1

    def setOutputFolder(self, output_folder_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.setOutputFolder")
        logg.info(f"Setting output_folder to '{output_folder_full}'")

        logui = logging.getLogger("UI")
        logui.info(f"Setting output folder to '{output_folder_full}'")

        # create the folder if it doesn't exist
        if not isdir(output_folder_full):
            logui.info(f"Not a folder '{output_folder_full}', creating it")
            makedirs(output_folder_full)

        self.output_folder.set(output_folder_full)

    def addInputFolder(self, input_folder_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.addInputFolder")
        logg.info(f"Adding new input_folder '{input_folder_full}'")

        logui = logging.getLogger("UI")

        # check for folder existence
        if not isdir(input_folder_full):
            logui.error(f"Not a valid folder: {input_folder_full}")
            return 1

        logui.info(f"Selected new input folder: '{input_folder_full}'")

        old_folders = self.input_folders.get()

        if input_folder_full in old_folders:
            logui.warn("Selected folder already in input list.")
            return 0

        old_folders[input_folder_full] = True
        self.input_folders.set(old_folders)

        self.updatePhotoInfoList()

    def toggleInputFolder(self, state):
        logg = logging.getLogger(f"c.{__class__.__name__}.toggleInputFolder")
        #  logg.setLevel("TRACE")
        logg.info("Setting new input_folder state")

        state = {x: state[x].get() for x in state}
        logg.trace(f"state {state}")

        if sum((state[x] for x in state)) > 0:
            # at least one still toggled
            self.input_folders.set(state)
        else:
            # no folders toggled, revert to previous state
            logui = logging.getLogger("UI")
            logui.warn("At least one input folder has to be selected.")
            self.input_folders._docallbacks()

        self.updatePhotoInfoList()

    def saveSelection(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.saveSelection")
        #  logg.setLevel("TRACE")
        logg.info("Saving selected pics")
        logui = logging.getLogger("UI")

        # check that output_folder is set
        output_folder = self.output_folder.get()
        if output_folder == self._out_fold_not_set:
            logui.warn("Set the output folder before saving the selection list")
            return

        # get current selection_list, {pic: [PhotoInfo, is_selected] }
        selection_list = self.selection_list.get()
        logg.trace(selection_list)

        # keep only selected
        active_selection = tuple(p for p in selection_list if selection_list[p][1])
        if len(active_selection) == 0:
            logui.warn("No active pic in selection list")
            return
        elif len(active_selection) == 1:
            s = ""
        else:
            s = "s"
        logui.info(f"Saving {len(active_selection)} pic{s} in {output_folder}")

        out_fol_content = set(listdir(output_folder))

        for pic in active_selection:
            base_pic = basename(pic)
            if base_pic in out_fol_content:
                logui.warn(f"{base_pic} already in output folder, skipping it")
                # MAYBE copy it with changed name
            else:
                copy2(pic, output_folder)

    def setLayout(self, lay_num):
        logg = logging.getLogger(f"c.{__class__.__name__}.setLayout")
        logg.info(f"Setting layout_current to '{lay_num}'")
        self.layout_current.set(lay_num)

        # if the new layout is not double, reset the values for meta_echo
        if not self.layout_current.get() in self._layout_is_double:
            self.metadata_echo.set(None)

    def cycleLayout(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.cycleLayout")
        #  logg.setLevel("TRACE")
        logg.info("Cycling layout")
        old_layout = self.layout_current.get()
        new_layout = (old_layout + 1) % self._layout_tot
        self.setLayout(new_layout)

        # if the new layout is double and the old is not, sync echo and prim indexes
        if new_layout in self._layout_is_double and (
            old_layout not in self._layout_is_double
        ):
            self.moveIndexEcho("sync")

    def swapDoubleLayout(self):
        """Go from a single to a double layout and back

        Save the current one if it's single, and go back to that
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.swapDoubleLayout")
        #  logg.setLevel("TRACE")
        logg.info("Swapping layout")
        # the layout is double: go back to saved single layout
        if self.layout_current.get() in self._layout_is_double:
            self.setLayout(self._old_single_layout)
        # the layout is single: save it and go to double
        else:
            self._old_single_layout = self.layout_current.get()
            self.setLayout(self._basic_double_layout)
            # also sync echo to prim
            self.moveIndexEcho("sync")

    def updatePhotoInfoList(self):
        """Update photo_info_list_active, load new photos and relative info

        photo_info_list_active is actually a dict of PhotoInfo objects
        Has to load the thumbnail and metadata
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.updatePhotoInfoList")
        #  logg.setLevel("TRACE")
        logg.info("Update photo_info_list_active")

        # list of filenames of active photos: ideally parallel to
        # photo_info_list_active.keys() but dict order can't be trusted so we
        # keep track here of the index
        # TODO the list passed to view to sort in special way
        # TODO sort list according to metadata
        # hopefully loading them will be fast, all will be needed to sort
        self._active_photo_list = []

        input_folders = self.input_folders.get()
        for folder in input_folders:
            # the folder is not toggled, skip it
            if input_folders[folder] is False:
                continue
            for photo in listdir(folder):
                photo_full = join(folder, photo)
                if self._is_photo(photo_full):
                    self._active_photo_list.append(photo_full)

        new_photo_info_active = {}
        for photo_full in self._active_photo_list:
            # load new photos in _photo_info_list_all
            if photo_full not in self._photo_info_list_all:
                self._photo_info_list_all[photo_full] = PhotoInfo(
                    photo_full, self._thumb_size
                )

            # collect the active PhotoInfo object in the new dict
            new_photo_info_active[photo_full] = self._photo_info_list_all[photo_full]

        logg.info(f"photo_info_list_active has now {len(new_photo_info_active)} items")

        logui = logging.getLogger("UI")
        logui.info(
            f"There are now {len(new_photo_info_active)} images in the active list."
        )

        self.photo_info_list_active.set(new_photo_info_active)

        current_photo_prim = self.current_photo_prim.get()
        if current_photo_prim in self._active_photo_list:
            # the photo is still in list: if needed update the index
            self._index_prim = self._active_photo_list.index(current_photo_prim)
        else:
            # the photo is not in list anymore: reset to 0
            self._index_prim = 0
            self._update_photo_prim(self._active_photo_list[0])

        # reset the echo index to follow prim
        self._index_echo = self._index_prim
        # reload the echo image
        self._update_photo_echo(self._active_photo_list[self._index_echo])

    def _is_photo(self, photo_full):
        _, photo_ext = splitext(photo_full)
        return photo_ext in self._is_photo_ext

    def setIndexPrim(self, index_prim):
        logg = logging.getLogger(f"c.{__class__.__name__}.setIndexPrim")
        logg.info(f"Setting index_prim to {index_prim}")
        self._index_prim = index_prim
        self._update_photo_prim(self._active_photo_list[index_prim])

    def moveIndexPrim(self, direction):
        logg = logging.getLogger(f"c.{__class__.__name__}.moveIndexPrim")
        logg.info(f"Moving index prim {direction}")
        if direction == "forward":
            new_index_prim = self._index_prim + 1
        elif direction == "backward":
            new_index_prim = self._index_prim - 1
        new_index_prim = new_index_prim % len(self.photo_info_list_active.get())
        self.setIndexPrim(new_index_prim)

    def seekIndexPrim(self, pic):
        logg = logging.getLogger(f"c.{__class__.__name__}.seekIndexPrim")
        logg.info("Seeking index prim")
        # MAYBE the pic is not in _active_photo_list... very weird, add guards?
        self._index_prim = self._active_photo_list.index(pic)
        self._update_photo_prim(pic)

    def _update_photo_prim(self, pic_prim):
        """Change what is needed for a new pic_prim

        - current_photo_prim
        - cropped_prim
        - prim metadata
        """
        logg = logging.getLogger(f"c.{__class__.__name__}._update_photo_prim")
        #  logg.setLevel("TRACE")
        logg.info(f"Updating photo prim, index {self._index_prim}")
        self.current_photo_prim.set(pic_prim)

        # resets zoom level and pos for the new photo; can only be done AFTER
        # mainloop starts, during initialization Model.doResize has not been
        # called yet, and the widget dimensions are still undefined;
        # the first time reset_image will be called by the Configure event later
        if self._widget_wid != -1:
            crop_prim = self._loaded_croppers.get_cropper(pic_prim)
            crop_prim.reset_image(self._widget_wid, self._widget_hei)
            self.cropped_prim.set(crop_prim.image_res)

            # if the layout is double, copy the new zoom level to echo pic
            if self.layout_current.get() in self._layout_is_double:
                self._cloneParams()

        # get the metadata for the image
        metadata_exif_prim = self._photo_info_list_all[pic_prim].get_metadata()
        metadata_named_prim = self._parse_metadata(metadata_exif_prim)
        self.metadata_prim.set(metadata_named_prim)

    def setIndexEcho(self, index_echo):
        logg = logging.getLogger(f"c.{__class__.__name__}.setIndexEcho")
        logg.info(f"Setting index_echo to {index_echo}")
        self._index_echo = index_echo
        self._update_photo_echo(self._active_photo_list[index_echo])

    def moveIndexEcho(self, direction):
        logg = logging.getLogger(f"c.{__class__.__name__}.moveIndexEcho")
        logg.info(f"Moving index echo {direction}")

        if not self.layout_current.get() in self._layout_is_double:
            # TODO move index prim in this case
            logg.warn("Current layout is not double, can't move index echo")
            return

        if direction == "forward":
            new_index_echo = self._index_echo + 1
        elif direction == "backward":
            new_index_echo = self._index_echo - 1
        elif direction == "sync":
            new_index_echo = self._index_prim

        new_index_echo = new_index_echo % len(self.photo_info_list_active.get())
        self.setIndexEcho(new_index_echo)

    def _update_photo_echo(self, pic_echo):
        """Change what is needed for a new pic_echo in echo frame

        - current_photo_echo
        - cropped_echo
        If _index_echo == _index_prim do not recompute image crop
        """
        logg = logging.getLogger(f"c.{__class__.__name__}._update_photo_echo")
        logg.info(f"Updating photo echo, index {self._index_echo}")
        self.current_photo_echo.set(pic_echo)

        if self._widget_wid != -1:
            self._cloneParams()

        if self.layout_current.get() in self._layout_is_double:
            # get the metadata for the image
            metadata_exif_echo = self._photo_info_list_all[pic_echo].get_metadata()
            metadata_named_echo = self._parse_metadata(metadata_exif_echo)
            self.metadata_echo.set(metadata_named_echo)
        else:
            self.metadata_echo.set(None)

    def likePressed(self, which_frame):
        """Update selection_list accordingly"""
        logg = logging.getLogger(f"c.{__class__.__name__}.likePressed")
        #  logg.setLevel("TRACE")
        logg.info(f"Like pressed on {which_frame}")

        # if the layout is not double consider the event from prim
        cur_lay_is_double = self.layout_current.get() in self._layout_is_double
        if (not cur_lay_is_double) and which_frame == "echo":
            which_frame = "prim"

        if which_frame == "prim":
            new_pic = self.current_photo_prim.get()
        elif which_frame == "echo":
            new_pic = self.current_photo_echo.get()
        else:
            logg.error(f"Unrecognized frame {which_frame}")

        old_selection_list = self.selection_list.get()

        if new_pic in old_selection_list:
            # if it was in selection_list already, toggle is_selected
            old_selection_list[new_pic][1] = not old_selection_list[new_pic][1]
        else:
            # add to dict (PhotoInfo, is_selected)
            old_selection_list[new_pic] = [self._photo_info_list_all[new_pic], True]

        self.selection_list.set(old_selection_list)

    def toggleSelectionPic(self, pic):
        logg = logging.getLogger(f"c.{__class__.__name__}.toggleSelectionPic")
        #  logg.setLevel("TRACE")
        logg.info(f"Toggling selection_list {pic}")

        old_selection_list = self.selection_list.get()
        old_selection_list[pic][1] = not old_selection_list[pic][1]
        self.selection_list.set(old_selection_list)

    def doResize(self, widget_wid, widget_hei):
        """Triggered by a configure event in the Label

        Also saves Label dimension, so that when the photo is changed, the new
        crop can be computed
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.doResize")
        #  logg.setLevel("TRACE")
        logg.info("Do resize")

        self._widget_wid = widget_wid
        self._widget_hei = widget_hei

        # get the current_photo_prim full name
        pic_prim = self.current_photo_prim.get()

        # reset the image with the new widget dimension:
        # get the cropper for the image
        crop_prim = self._loaded_croppers.get_cropper(pic_prim)
        # reset the image zoom/pos
        crop_prim.reset_image(self._widget_wid, self._widget_hei)
        # update the Observable
        self.cropped_prim.set(crop_prim.image_res)

        if self.layout_current.get() in self._layout_is_double:
            # clone params to echo
            self._cloneParams()

    def zoomImage(self, direction, rel_x=-1, rel_y=-1):
        logg = logging.getLogger(f"c.{__class__.__name__}.zoomImage")
        #  logg.setLevel("TRACE")
        logg.trace(f"Zooming in direction {direction}")
        # get current prim pic
        pic_prim = self.current_photo_prim.get()
        # get the cropper for the image
        crop_prim = self._loaded_croppers.get_cropper(pic_prim)
        # zoom the image
        crop_prim.zoom_image(direction, rel_x, rel_y)
        # update the Observable
        self.cropped_prim.set(crop_prim.image_res)

        if self.layout_current.get() in self._layout_is_double:
            self._cloneParams()

    def moveImageDirection(self, direction):
        """Move image in the specified direction of self._mov_delta"""
        logg = logging.getLogger(f"c.{__class__.__name__}.moveImageDirection")
        #  logg.setLevel("TRACE")
        logg.trace(f"Moving in direction {direction}")
        if direction == "right":
            self._moveImage(self._mov_delta, 0)
        elif direction == "left":
            self._moveImage(-self._mov_delta, 0)
        elif direction == "up":
            self._moveImage(0, -self._mov_delta)
        elif direction == "down":
            self._moveImage(0, self._mov_delta)

    def moveImageMouse(self, mouse_x, mouse_y):
        """Move the image to follow the mouse"""
        logg = logging.getLogger(f"c.{__class__.__name__}.moveImageMouse")
        #  logg.setLevel("TRACE")
        logg.trace("Moving mouse")
        delta_x = self._old_mouse_x - mouse_x
        delta_y = self._old_mouse_y - mouse_y
        self._old_mouse_x = mouse_x
        self._old_mouse_y = mouse_y
        self._moveImage(delta_x, delta_y)

    def saveMousePos(self, mouse_x, mouse_y):
        """Save the current mouse position"""
        self._old_mouse_x = mouse_x
        self._old_mouse_y = mouse_y

    def _moveImage(self, delta_x, delta_y):
        """Actually move image of specified delta"""
        logg = logging.getLogger(f"c.{__class__.__name__}._moveImage")
        #  logg.setLevel("TRACE")
        logg.trace(f"Moving delta {delta_x} {delta_y}")
        # get current prim pic
        pic_prim = self.current_photo_prim.get()
        # get the cropper for the image
        crop_prim = self._loaded_croppers.get_cropper(pic_prim)
        # move the image
        crop_prim.move_image(delta_x, delta_y)
        # update the Observable
        self.cropped_prim.set(crop_prim.image_res)

        # if double, move echo as well
        if self.layout_current.get() in self._layout_is_double:
            self._cloneParams()

    def _cloneParams(self):
        """Clone current prim params to echo image"""
        # MAYBE the check for doubleness of the layout can be done here
        # cloning only makes sense if it's double after all
        logg = logging.getLogger(f"c.{__class__.__name__}._cloneParams")
        #  logg.setLevel("TRACE")
        logg.trace("Cloning params")

        # get current prim pic
        pic_prim = self.current_photo_prim.get()
        # get the cropper for the image
        crop_prim = self._loaded_croppers.get_cropper(pic_prim)

        # get current echo pic
        pic_echo = self.current_photo_echo.get()
        # get the cropper for the image
        crop_echo = self._loaded_croppers.get_cropper(pic_echo)

        # get params from prim
        params = crop_prim.get_params()
        # copy them in echo
        crop_echo.load_params(params)
        # update echo observable
        self.cropped_echo.set(crop_echo.image_res)

    def _load_named_metadata(self):
        """Populate two dicts that map a readable name in the metadata field"""
        self.name2exif = {}
        self.name2exif["Date taken"] = "Image DateTime"
        #  "EXIF DateTimeOriginal",
        #  "EXIF DateTimeDigitized",
        self.name2exif["Exposure time"] = "EXIF ExposureTime"
        self.name2exif["Aperture"] = "EXIF FNumber"
        #  self.name2exif["Program"] = "EXIF ExposureProgram"
        self.name2exif["ISO"] = "EXIF ISOSpeedRatings"
        self.name2exif["Width"] = "PILWidth"
        self.name2exif["Height"] = "PILHeight"

    def _parse_metadata(self, metadata_exif):
        """Parse raw EXIF metadata into named ones"""
        logg = logging.getLogger(f"c.{__class__.__name__}._parse_metadata")
        #  logg.setLevel("TRACE")
        logg.info("Parsing metadata")

        metadata_named = {}
        # translate the names from EXIF to readable, set default values
        for name in self.name2exif:
            exif_name = self.name2exif[name]
            if exif_name in metadata_exif:
                if name == "Aperture":
                    logg.trace(f"{str(metadata_exif[exif_name])}")
                    fra = Fraction(str(metadata_exif[exif_name]))
                    metadata_named[name] = fra.numerator / fra.denominator
                else:
                    metadata_named[name] = metadata_exif[exif_name]
            else:
                metadata_named[name] = "-"
            logg.trace(f"{name}: {metadata_named[name]}")

        return metadata_named


class ModelCrop:
    def __init__(self, photo_name_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info("Start init")

        self._photo_name_full = photo_name_full
        self._image = Image.open(self._photo_name_full)
        self._image_wid, self._image_hei = self._image.size

        # https://stackoverflow.com/a/51245891/2237151
        logg.trace(f"{photo_name_full} size: {getsizeof(self._image.tobytes())}")

        # setup parameters for resizing
        self.upscaling_mode = Image.NEAREST
        self.downscaling_mode = Image.LANCZOS

        # zoom saved in logg scale, actual zoom: zoom_base**zoom_level
        self._zoom_base = sqrt(2)
        self._zoom_level = None

        self._mov_x = 0
        self._mov_y = 0

    def reset_image(self, widget_wid=-1, widget_hei=-1):
        """Resets zoom level and position of the image

        Save the current widget dimensions if changed.

        Find zoom_level so that the image fits in the widget:
        _image_wid * ( zoom_base ** zoom_level ) = widget_wid
        and analogously for hei
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.reset_image")
        #  logg.setLevel("TRACE")
        logg.trace("Resetting image")
        if widget_wid != -1:
            self.widget_wid = widget_wid
            self.widget_hei = widget_hei

        if self._image_wid < self.widget_wid and self._image_hei < self.widget_hei:
            # the original photo is smaller than the widget
            self._zoom_level = 0
        else:
            ratio = min(
                self.widget_wid / self._image_wid, self.widget_hei / self._image_hei
            )
            self._zoom_level = log(ratio, self._zoom_base)

        self._mov_x = 0
        self._mov_y = 0
        self.update_crop()

    def update_crop(self):
        """Update the cropped region with the current parameters

        Image.resize takes as args
        - the output dimension (wid, hei)
        - the region to crop from (left, top, right, bottom)

        The Label fills the frame, and the image is centered in the Label,
        there is no need for x_pos and place
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_crop")
        #  logg.setLevel("TRACE")
        logg.trace(f"Updating crop zoom {self._zoom_level:.4f}")

        # zoom in linear scale
        zoom = self._zoom_base ** self._zoom_level

        # dimension of the virtual zoomed image
        zoom_wid = ceil(self._image_wid * zoom)
        zoom_hei = ceil(self._image_hei * zoom)

        # the zoomed photo fits inside the widget
        if zoom_wid <= self.widget_wid and zoom_hei <= self.widget_hei:
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            # take the entire image
            region = [0, 0, self._image_wid, self._image_hei]

        # the zoomed photo is wider than the widget
        elif zoom_wid > self.widget_wid and zoom_hei <= self.widget_hei:
            # target dimension as wide as the widget
            resized_dim = (self.widget_wid, zoom_hei)
            # from top to bottom, only keep a vertical stripe
            region = [
                self._mov_x / zoom,
                0,
                (self._mov_x + self.widget_wid) / zoom,
                self._image_hei,
            ]

        # the zoomed photo is taller than the widget
        elif zoom_wid <= self.widget_wid and zoom_hei > self.widget_hei:
            resized_dim = (zoom_wid, self.widget_hei)
            region = [
                0,
                self._mov_y / zoom,
                self._image_wid,
                (self._mov_y + self.widget_hei) / zoom,
            ]

        # the zoomed photo is bigger than the widget
        elif zoom_wid > self.widget_wid and zoom_hei > self.widget_hei:
            resized_dim = (self.widget_wid, self.widget_hei)
            region = [
                self._mov_x / zoom,
                self._mov_y / zoom,
                (self._mov_x + self.widget_wid) / zoom,
                (self._mov_y + self.widget_hei) / zoom,
            ]

        self._validate_region(region)
        logg.trace(f"resized_dim {resized_dim} region {region}")

        # decide what method to use when resizing
        if zoom > 1:
            resampling_mode = self.upscaling_mode
        else:
            resampling_mode = self.downscaling_mode

        # apply resize
        image_res = self._image.resize(resized_dim, resampling_mode, region)
        # convert the photo for tkinter
        image_res = ImageTk.PhotoImage(image_res)
        # save it as attribute of the object, not garbage collected
        self.image_res = image_res

    def zoom_image(self, direction, rel_x=-1, rel_y=-1):
        """Change zoom level, keep (rel_x, rel_y) still"""
        logg = logging.getLogger(f"c.{__class__.__name__}.zoom_image")
        #  logg.setLevel("TRACE")
        logg.info(f"Zooming image {direction}")

        old_zoom = self._zoom_base ** self._zoom_level
        old_zoom_wid = self._image_wid * old_zoom
        old_zoom_hei = self._image_hei * old_zoom

        if direction == "in":
            self._zoom_level += 1
        elif direction == "out":
            self._zoom_level -= 1
        elif direction == "reset":
            self.reset_image()
            return 0
        else:
            logg.error(f"Unrecognized zooming direction {direction}")
            return 1

        new_zoom = self._zoom_base ** self._zoom_level
        new_zoom_wid = self._image_wid * new_zoom
        new_zoom_hei = self._image_hei * new_zoom
        logg.trace(f"old_zoom {old_zoom} new_zoom {new_zoom}")
        recap = f"image ({self._image_wid}, {self._image_hei})"
        recap += f" old_zoom ({old_zoom_wid}, {old_zoom_hei})"
        recap += f" new_zoom ({new_zoom_wid}, {new_zoom_hei})"
        logg.trace(recap)

        # find the center of the photo on the screen if not set
        if rel_x == -1 or rel_y == -1:
            if old_zoom_wid < self.widget_wid and old_zoom_hei < self.widget_hei:
                rel_x = old_zoom_wid / 2
                rel_y = old_zoom_hei / 2
            elif old_zoom_wid >= self.widget_wid and old_zoom_hei < self.widget_hei:
                rel_x = self.widget_wid / 2
                rel_y = old_zoom_hei / 2
            elif old_zoom_wid < self.widget_wid and old_zoom_hei >= self.widget_hei:
                rel_x = old_zoom_wid / 2
                rel_y = self.widget_hei / 2
            elif old_zoom_wid >= self.widget_wid and old_zoom_hei >= self.widget_hei:
                rel_x = self.widget_wid / 2
                rel_y = self.widget_hei / 2
        recap = f"rel_x {rel_x} rel_y {rel_y}"
        recap += f" widget ({self.widget_wid}, {self.widget_hei})"
        logg.trace(recap)
        recap = f"mov_x/old_zoom {self._mov_x / old_zoom}"
        recap += f" mov_x/new_zoom {self._mov_x / new_zoom}"
        recap += f" rel_x/old_zoom {rel_x / old_zoom}"
        recap += f" rel_x/new_zoom {rel_x / new_zoom}"
        logg.trace(recap)
        recap = f"(mov_x+rel_x)*new_z/old_z {(self._mov_x+rel_x)*new_zoom/old_zoom}"
        recap += f" (mov_y+rel_y)*new_z/old_z {(self._mov_y+rel_y)*new_zoom/old_zoom}"
        logg.trace(recap)

        # source of hell was that the formula *is* right, but sometimes to keep
        # a point fixed you need *negative* mov_x, implemented by moving the
        # Label around; this will not happen, and mov can be set to 0.
        # the same happens on the other side, the region should go out of the image
        new_mov_x = (self._mov_x + rel_x) * new_zoom / old_zoom - rel_x
        new_mov_y = (self._mov_y + rel_y) * new_zoom / old_zoom - rel_y

        if new_zoom_wid < self.widget_wid and new_zoom_hei < self.widget_hei:
            logg.trace(f'new_zoom photo {format_color("smaller", "green")} than frame')
            self._mov_x = 0
            self._mov_y = 0
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei < self.widget_hei:
            logg.trace(f'new_zoom photo {format_color("wider", "green")} than frame')
            self._mov_x = new_mov_x
            self._mov_y = 0
        elif new_zoom_wid < self.widget_wid and new_zoom_hei >= self.widget_hei:
            logg.trace(f'new_zoom photo {format_color("taller", "green")} than frame')
            self._mov_x = 0
            self._mov_y = new_mov_y
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei >= self.widget_hei:
            logg.trace(f'new_zoom photo {format_color("larger", "green")} than frame')
            self._mov_x = new_mov_x
            self._mov_y = new_mov_y

        self._validate_mov()

        recap = f"mov_x {self._mov_x} mov_y {self._mov_y}"
        logg.trace(recap)

        self.update_crop()

    def get_params(self):
        """Returns all the relevant params for the pic

        Basically everything that is not set in __init__ has to be copied
        """
        params = {}
        params["mov_x"] = self._mov_x
        params["mov_y"] = self._mov_y
        params["zoom_level"] = self._zoom_level
        params["widget_wid"] = self.widget_wid
        params["widget_hei"] = self.widget_hei
        return params

    def load_params(self, params):
        """Crop the photo according to params"""
        self._mov_x = params["mov_x"]
        self._mov_y = params["mov_y"]
        self._zoom_level = params["zoom_level"]
        self.widget_wid = params["widget_wid"]
        self.widget_hei = params["widget_hei"]
        # MAYBE do validation on params, pic might be of different size
        self.update_crop()

    def move_image(self, delta_x, delta_y):
        """Move image of specified delta"""
        self._mov_x += delta_x
        self._mov_y += delta_y
        self._validate_mov()
        self.update_crop()

    def _validate_mov(self):
        """Check that mov is reasonable for the current widget/image/zoom"""
        zoom = self._zoom_base ** self._zoom_level
        zoom_wid = self._image_wid * zoom
        zoom_hei = self._image_hei * zoom

        # in any case they can't be negative
        if self._mov_x < 0:
            self._mov_x = 0
        if self._mov_y < 0:
            self._mov_y = 0

        # the zoomed photo fits inside the widget
        if zoom_wid < self.widget_wid and zoom_hei < self.widget_hei:
            self._mov_x = 0
            self._mov_y = 0
        # the zoomed photo is wider than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei < self.widget_hei:
            if self._mov_x + self.widget_wid > zoom_wid:
                self._mov_x = zoom_wid - self.widget_wid
            self._mov_y = 0
        # the zoomed photo is taller than the widget
        elif zoom_wid < self.widget_wid and zoom_hei >= self.widget_hei:
            self._mov_x = 0
            if self._mov_y + self.widget_hei > zoom_hei:
                self._mov_y = zoom_hei - self.widget_hei
        # the zoomed photo is bigger than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei >= self.widget_hei:
            if self._mov_x + self.widget_wid > zoom_wid:
                self._mov_x = zoom_wid - self.widget_wid
            if self._mov_y + self.widget_hei > zoom_hei:
                self._mov_y = zoom_hei - self.widget_hei

    def _validate_region(self, region):
        """region (left, top, right, bottom) must fit inside the image"""
        # left
        if region[0] < 0:
            region[0] = 0
        # top
        if region[1] < 0:
            region[1] = 0
        # right
        if region[2] > self._image_wid:
            region[2] = self._image_wid
        # bottom
        if region[3] > self._image_hei:
            region[3] = self._image_hei


class Holder:
    """Basic interface for a Holder, that might work in the future as a LRU cache

    The implementation will be a dict for now
    """

    def __init__(self, cache_dim):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info("Start init")

        self._loaded_croppers = {}

    def get_cropper(self, image_name):
        """Return the requested cropper, if not loaded, create it on the fly"""
        logg = logging.getLogger(f"c.{__class__.__name__}.get_cropper")
        logg.trace("Getting cropper")

        if image_name not in self._loaded_croppers:
            self._load_cropper(image_name)

        return self._loaded_croppers[image_name]

    def _load_cropper(self, image_name):
        """Load the cropper"""
        logg = logging.getLogger(f"c.{__class__.__name__}._load_cropper")
        logg.info("Loading cropper")

        self._loaded_croppers[image_name] = ModelCrop(image_name)
