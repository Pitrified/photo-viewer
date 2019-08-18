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
from utils import format_color


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
        self._widget_wid = -1
        self._widget_hei = -1

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

        # load the image if needed
        if not pic in self._croppers_prim:
            log.info("Loaded in _update_photo_prim")
            self._croppers_prim[pic] = ModelCrop(pic, self.cropped_prim)

        # resets zoom level and pos for the new photo; can only be done AFTER
        # mainloop starts, during initialization Model.doResize has not been
        # called yet, and the widget dimensions are still undefined;
        # the first time reset_image will be called by the Configure event later
        if self._widget_wid != -1:
            self._croppers_prim[pic].reset_image(self._widget_wid, self._widget_hei)

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
        """Triggered by a configure event in the Label

        Also saves Label dimension, so that when the photo is changed, the new
        crop can be computed
        """
        log = logging.getLogger(f"c.{__class__.__name__}.doResize")
        log.info("Do resize")

        self._widget_wid = widget_wid
        self._widget_hei = widget_hei

        # get the current_photo_prim full name
        pic = self.current_photo_prim.get()

        # load the photo if needed
        if not pic in self._croppers_prim:
            log.info("Loaded in doResize")
            self._croppers_prim[pic] = ModelCrop(pic, self.cropped_prim)

        self._croppers_prim[pic].reset_image(self._widget_wid, self._widget_hei)

        if self.layout_current.get() in self._layout_is_double:
            self.current_photo_echo.get()

    def zoomImage(self, direction, rel_x=-1, rel_y=-1):
        pic = self.current_photo_prim.get()

        self._croppers_prim[pic].zoom_image(direction, rel_x, rel_y)

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
        #  self._zoom_base = 2
        self._zoom_level = None

        self._mov_x = 0
        self._mov_y = 0
        # you move delta pixel regardless of zoom_level
        # when zooming the function will take care of leaving a fixed point
        # MAYBE the fixed point for zoom from keyboard should be the midpoint
        self._mov_delta = 50

    def reset_image(self, widget_wid=-1, widget_hei=-1):
        """Resets zoom level and position of the image

        Save the current widget dimensions if changed.

        Find zoom_level so that the image fits in the widget:
        _image_wid * ( zoom_base ** zoom_level ) = widget_wid
        and analogously for hei
        """
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
        log = logging.getLogger(f"c.{__class__.__name__}.update_crop")
        log.setLevel("TRACE")
        log.info(f"Updating crop zoom {self._zoom_level:.4f}")

        # zoom in linear scale
        zoom = self._zoom_base ** self._zoom_level

        # dimension of the virtual zoomed image
        zoom_wid = ceil(self._image_wid * zoom)
        zoom_hei = ceil(self._image_hei * zoom)

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
                self._mov_x / zoom,
                self._mov_y / zoom,
                (self._mov_x + self.widget_wid) / zoom,
                (self._mov_y + self.widget_hei) / zoom,
            )

        # apply resize
        log.debug(f"resized_dim {resized_dim} region {region}")
        image_res = self._image.resize(resized_dim, self.resampling_mode, region)
        # convert the photo for tkinter
        image_res = ImageTk.PhotoImage(image_res)
        # save it in the observable, not garbage collected
        self._image_observable.set(image_res)

    def zoom_image(self, direction, rel_x=-1, rel_y=-1):
        """Change zoom level, keep (rel_x, rel_y) still
        """
        log = logging.getLogger(f"c.{__class__.__name__}.zoom_image")
        log.setLevel("TRACE")
        log.info("Zooming image {direction}")

        old_zoom = self._zoom_base ** self._zoom_level
        old_zoom_wid = self._image_wid * old_zoom
        old_zoom_hei = self._image_hei * old_zoom

        if direction == "in":
            self._zoom_level += 1
        elif direction == "out":
            self._zoom_level -= 1
        elif direction == "reset":
            self.reset_image()
        else:
            log.error(f"Unrecognized zooming direction {direction}")
            return 1

        new_zoom = self._zoom_base ** self._zoom_level
        new_zoom_wid = self._image_wid * new_zoom
        new_zoom_hei = self._image_hei * new_zoom
        log.trace(f"old_zoom {old_zoom} new_zoom {new_zoom}")
        recap = f" image ({self._image_wid}, {self._image_hei})"
        recap += f" old_zoom ({old_zoom_wid}, {old_zoom_hei})"
        recap += f" new_zoom ({new_zoom_wid}, {new_zoom_hei})"
        log.trace(recap)

        # find the center of the photo on the screen if not set
        # EVERYTHING wrong:
        # the ifs must be done on old_zoom
        # old_zoom_wid>widget_wid -> mov_x must be considered
        # prolly rel_x = widget_wid / 2 + mov_x/zoom
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
        log.trace(recap)
        recap = f"mov_x/old_zoom {self._mov_x / old_zoom}"
        recap += f" mov_x/new_zoom {self._mov_x / new_zoom}"
        recap += f" rel_x/old_zoom {rel_x / old_zoom}"
        recap += f" rel_x/new_zoom {rel_x / new_zoom}"
        log.trace(recap)
        recap = (
            f"(mov_x+rel_x)*new_zoom/old_zoom {(self._mov_x+rel_x)*new_zoom/old_zoom}"
        )
        log.trace(recap)

        # MORE errors:
        # mov_x is already in the *zoomed* image, mov_x/zoom is on the real one
        # when you remove rel_x and the photo now goes outside, you are not
        # removing enough
        if new_zoom_wid < self.widget_wid and new_zoom_hei < self.widget_hei:
            log.trace(f'new_zoom photo {format_color("smaller", "green")} than frame')
            self._mov_x = 0
            self._mov_y = 0
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei < self.widget_hei:
            log.trace(f'new_zoom photo {format_color("wider", "green")} than frame')
            #  self._mov_x = (
            #  self._mov_x / old_zoom + rel_x / old_zoom - rel_x / new_zoom
            #  ) * new_zoom
            self._mov_x = (self._mov_x + rel_x) * new_zoom / old_zoom - self.widget_wid/2
            self._mov_y = 0
        elif new_zoom_wid < self.widget_wid and new_zoom_hei >= self.widget_hei:
            log.trace(f'new_zoom photo {format_color("taller", "green")} than frame')
            self._mov_x = 0
            #  self._mov_y = (
            #  self._mov_y / old_zoom + rel_y / old_zoom - rel_y / new_zoom
            #  ) * new_zoom
            self._mov_y = (self._mov_y + rel_y) * new_zoom / old_zoom - self.widget_hei/2
        elif new_zoom_wid >= self.widget_wid and new_zoom_hei >= self.widget_hei:
            log.trace(f'new_zoom photo {format_color("larger", "green")} than frame')
            #  self._mov_x = (
            #  self._mov_x / old_zoom + rel_x / old_zoom - rel_x / new_zoom
            #  ) * new_zoom
            #  self._mov_y = (
            #  self._mov_y / old_zoom + rel_y / old_zoom - rel_y / new_zoom
            #  ) * new_zoom
            self._mov_x = (self._mov_x + rel_x) * new_zoom / old_zoom - self.widget_wid/2
            self._mov_y = (self._mov_y + rel_y) * new_zoom / old_zoom - self.widget_hei/2

        self.update_crop()
