import logging

from PIL import Image
from PIL import ImageTk
from os import listdir
from os.path import join
from os.path import splitext
from math import sqrt
from math import log
from math import floor
from math import ceil

from observable import Observable
from photo_info import PhotoInfo


class Model:
    def __init__(self):
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        self.output_folder = Observable("Not set not known")
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

        self._is_photo_ext = set((".jpg", ".jpeg", ".JPG", ".png"))
        self._thumb_size = 50

        self.cropped_prim = Observable(None)
        #  self.cropper_photo_prim = ModelCrop()
        # MAYBE this could be a Queue to remember previous photo
        self._croppers_prim = {}

        # setup layout info
        self._layout_tot = 5
        self._layout_is_double = (1,)
        self.layout_current = Observable(0)
        #  self.layout_set(self.layout_current)

    def setOutputFolder(self, output_folder_full):
        log = logging.getLogger(f"c.{__class__.__name__}.setOutputFolder")
        log.info(f"Setting output_folder to '{output_folder_full}'")
        self.output_folder.set(output_folder_full)

    def addInputFolder(self, input_folder_full):
        log = logging.getLogger(f"c.{__class__.__name__}.addInputFolder")
        log.info(f"Adding new input_folder '{input_folder_full}'")

        old_folders = self.input_folders.get()

        if input_folder_full in old_folders:
            log.info("Folder already in input list")
            return

        old_folders[input_folder_full] = True
        self.input_folders.set(old_folders)

        self.updatePhotoInfoList()

    def toggleInputFolder(self, state):
        log = logging.getLogger(f"c.{__class__.__name__}.toggleInputFolder")
        #  log.setLevel("TRACE")
        log.info(f"Setting new input_folder state")

        state = {x: state[x].get() for x in state}
        log.trace(f"state {state}")

        if sum((state[x] for x in state)) > 0:
            # at least one still toggled
            self.input_folders.set(state)
        else:
            # no folders toggled, revert to previous state
            log.warn("At least one input folder has to be selected")
            self.input_folders._docallbacks()

        self.updatePhotoInfoList()

    def setLayout(self, lay_num):
        log = logging.getLogger(f"c.{__class__.__name__}.setLayout")
        log.info(f"Setting layout_current to '{lay_num}'")
        self.layout_current.set(lay_num)

    def cycleLayout(self):
        log = logging.getLogger(f"c.{__class__.__name__}.cycleLayout")
        #  log.setLevel("TRACE")
        log.info("Cycling layout")
        old_layout = self.layout_current.get()
        new_layout = (old_layout + 1) % self._layout_tot
        self.layout_current.set(new_layout)

        # if the new layout is double and the old is not, sync echo and prim indexes
        if new_layout in self._layout_is_double and (
            not old_layout in self._layout_is_double
        ):
            self.setIndexEcho(self._index_prim)

    def updatePhotoInfoList(self):
        """Update photo_info_list_active, load new photos and relative info

        photo_info_list_active is actually a dict of PhotoInfo objects
        Has to load the thumbnail and metadata
        """
        log = logging.getLogger(f"c.{__class__.__name__}.updatePhotoInfoList")
        log.setLevel("TRACE")
        log.info(f"Update photo_info_list_active")

        # list of filenames of active photos: ideally parallel to
        # photo_info_list_active.keys() but dict order can't be trusted so we
        # keep track here of the index
        # MAYBE the list passed to view to sort in special way
        self._active_photo_list = []

        input_folders = self.input_folders.get()
        for folder in input_folders:
            # the folder is not toggled, skip it
            if input_folders[folder] == False:
                continue
            for photo in listdir(folder):
                photo_full = join(folder, photo)
                if self._is_photo(photo_full):
                    self._active_photo_list.append(photo_full)

        new_photo_info_active = {}
        for photo_full in self._active_photo_list:
            # load new photos in _photo_info_list_all
            if not photo_full in self._photo_info_list_all:
                self._photo_info_list_all[photo_full] = PhotoInfo(
                    photo_full, self._thumb_size
                )

            # collect the active PhotoInfo object in the new dict
            new_photo_info_active[photo_full] = self._photo_info_list_all[photo_full]

        log.debug(f"photo_info_list_active has now {len(new_photo_info_active)} items")
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
        if photo_ext in self._is_photo_ext:
            return True
        else:
            return False

    def setIndexPrim(self, index_prim):
        log = logging.getLogger(f"c.{__class__.__name__}.setIndexPrim")
        log.info(f"Setting index_prim to {index_prim}")
        self._index_prim = index_prim
        self._update_photo_prim(self._active_photo_list[index_prim])

    def moveIndexPrim(self, direction):
        log = logging.getLogger(f"c.{__class__.__name__}.moveIndexPrim")
        log.info(f"Moving index prim {direction}")
        if direction == "forward":
            new_index_prim = self._index_prim + 1
        elif direction == "backward":
            new_index_prim = self._index_prim - 1
        self._index_prim = new_index_prim % len(self.photo_info_list_active.get())
        self._update_photo_prim(self._active_photo_list[self._index_prim])

    def seekIndexPrim(self, pic):
        log = logging.getLogger(f"c.{__class__.__name__}.seekIndexPrim")
        log.info(f"Seeking index prim")
        self._index_prim = self._active_photo_list.index(pic)
        self._update_photo_prim(pic)

    def _update_photo_prim(self, pic):
        """Change what is needed for a new pic

        - current_photo_prim
        - cropped_prim
        """
        log = logging.getLogger(f"c.{__class__.__name__}._update_photo_prim")
        self.current_photo_prim.set(pic)

        if not pic in self._croppers_prim:
            log.info("Loaded in _update_photo_prim")
            self._croppers_prim[pic] = ModelCrop(pic, self.cropped_prim)

    def setIndexEcho(self, index_echo):
        log = logging.getLogger(f"c.{__class__.__name__}.setIndexEcho")
        log.info(f"Setting index_echo to {index_echo}")
        self._index_echo = index_echo
        self._update_photo_echo(self._active_photo_list[index_echo])

    def moveIndexEcho(self, direction):
        log = logging.getLogger(f"c.{__class__.__name__}.moveIndexEcho")
        log.info(f"Moving index echo {direction}")

        if not self.layout_current.get() in self._layout_is_double:
            log.warn("Current layout is not double, can't move index echo")
            return

        if direction == "forward":
            new_index_echo = self._index_echo + 1
        elif direction == "backward":
            new_index_echo = self._index_echo - 1
        self._index_echo = new_index_echo % len(self.photo_info_list_active.get())
        self._update_photo_echo(self._active_photo_list[self._index_echo])

    def _update_photo_echo(self, pic):
        """Change what is needed for a new pic in echo frame

        - current_photo_echo
        - cropped_echo
        If _index_echo == _index_prim do not recompute image crop
        """
        log = logging.getLogger(f"c.{__class__.__name__}._update_photo_echo")
        log.trace(f"Updating photo echo, index {self._index_echo}")
        self.current_photo_echo.set(pic)

    def likePressed(self, which_frame):
        """Update selection_list accordingly
        """
        log = logging.getLogger(f"c.{__class__.__name__}.likePressed")
        log.setLevel("TRACE")
        log.info(f"Like pressed on {which_frame}")

        # if the layout is not double consider the event from prim
        cur_lay_is_double = self.layout_current.get() in self._layout_is_double
        if (not cur_lay_is_double) and which_frame == "l":
            which_frame = "k"

        if which_frame == "k":
            new_pic = self.current_photo_prim.get()
        elif which_frame == "l":
            new_pic = self.current_photo_echo.get()
        else:
            log.error(f"Unrecognized frame {which_frame}")

        old_selection_list = self.selection_list.get()

        if new_pic in old_selection_list:
            # if it was in selection_list already, toggle is_selected
            old_selection_list[new_pic][1] = not old_selection_list[new_pic][1]
        else:
            # add to dict (PhotoInfo, is_selected)
            old_selection_list[new_pic] = [self._photo_info_list_all[new_pic], True]

        self.selection_list.set(old_selection_list)

    def toggleSelectionPic(self, pic):
        log = logging.getLogger(f"c.{__class__.__name__}.toggleSelectionPic")
        #  log.setLevel("TRACE")
        log.info(f"Toggling selection_list {pic}")

        old_selection_list = self.selection_list.get()
        old_selection_list[pic][1] = not old_selection_list[pic][1]
        self.selection_list.set(old_selection_list)

    def doResize(self, widget_wid, widget_hei):
        log = logging.getLogger(f"c.{__class__.__name__}.doResize")
        log.info("Do resize")

        cur_ph_prim = self.current_photo_prim.get()

        # load the photo if needed
        if not cur_ph_prim in self._croppers_prim:
            log.info("Loaded in doResize")
            self._croppers_prim[cur_ph_prim] = ModelCrop(cur_ph_prim, self.cropped_prim)

        self._croppers_prim[cur_ph_prim].do_resize(widget_wid, widget_hei)

        if self.layout_current.get() in self._layout_is_double:
            self.current_photo_echo.get()


class ModelCrop:
    def __init__(self, photo_name_full, image_observable):
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        self._photo_name_full = photo_name_full
        self._image_observable = image_observable
        self._image = Image.open(self._photo_name_full)
        self._image_wid, self._image_hei = self._image.size

        # setup parameters for resizing
        self.resampling_mode = Image.NEAREST

        # zoom saved in log scale, actual zoom: zoom_base**zoom_level
        self._zoom_base = sqrt(2)
        self._zoom_level = None

        self._mov_x = 0
        self._mov_y = 0
        # you move delta pixel regardless of zoom_level
        # when zooming the function will take care of leaving a fixed point
        # MAYBE the fixed point for zoom from keyboard should be the midpoint
        self._mov_delta = 50

    def reset_zoom_level(self, widget_wid, widget_hei):
        """Find zoom_level so that the image fits in the widget

        _image_wid * ( zoom_base ** zoom_level ) = widget_wid
        and analogously for hei
        """
        if self._image_wid < widget_wid and self._image_hei < widget_hei:
            # the original photo is smaller than the widget
            self._zoom_level = 0
        else:
            ratio = min(widget_wid / self._image_wid, widget_hei / self._image_hei)
            self._zoom_level = log(ratio, self._zoom_base)

    def do_resize(self, widget_wid, widget_hei):
        """React to the widget changing dimension

        Resets zoom level and position
        Save the current widget dimensions
        """
        self.reset_zoom_level(widget_wid, widget_hei)
        self._mov_x = 0
        self._mov_y = 0
        self.widget_wid = widget_wid
        self.widget_hei = widget_hei

        self.update_crop()

    def update_crop(self):
        """Update the cropped region with the current parameters

        Image.resize takes as args
        - the output dimension (wid, hei)
        - the region to crop from (left, top, right, bottom)

        The Label fills the frame, and the image is centered in the Label,
        there is no need for x_pos and place
        """
        # zoom in linear scale
        zoom = self._zoom_base ** self._zoom_level

        # dimension of the virtual zoomed image
        zoom_wid = floor(self._image_wid * zoom)
        zoom_hei = floor(self._image_hei * zoom)

        # the zoomed photo fits inside the widget
        if zoom_wid < self.widget_wid and zoom_hei < self.widget_hei:
            # resize the pic, don't cut it
            resized_dim = (zoom_wid, zoom_hei)
            # take the entire image
            region = (0, 0, self._image_wid, self._image_hei)

        # the zoomed photo is wider than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei < self.widget_hei:
            # target dimension as wide as the widget
            resized_dim = (self.widget_wid, zoom_hei)
            # from top to bottom, only keep a vertical stripe
            region = (
                self._mov_x / zoom,
                0,
                (self._mov_x + self.widget_wid) / zoom,
                self._image_hei,
            )

        # the zoomed photo is taller than the widget
        elif zoom_wid < self.widget_wid and zoom_hei >= self.widget_hei:
            resized_dim = (zoom_wid, self.widget_hei)
            region = (
                0,
                self._mov_y / zoom,
                self._image_wid,
                (self._mov_y + self.widget_hei) / zoom,
            )

        # the zoomed photo is bigger than the widget
        elif zoom_wid >= self.widget_wid and zoom_hei >= self.widget_hei:
            resized_dim = (self.widget_wid, self.widget_hei)
            region = (
                self.mov_x / zoom,
                self.mov_y / zoom,
                (self.mov_x + self.widget_wid) / zoom,
                (self.mov_y + self.widget_hei) / zoom,
            )

        # apply resize
        image_res = self._image.resize(resized_dim, self.resampling_mode, region)
        # convert the photo for tkinter
        image_res = ImageTk.PhotoImage(image_res)
        # save it in the observable, not garbage collected
        self._image_observable.set(image_res)
