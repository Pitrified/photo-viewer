import logging

from PIL import Image
from os import listdir
from os.path import join
from os.path import splitext

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

        self.current_photo_prim = Observable("")
        self._index_prim = 0
        self.current_photo_echo = Observable("")
        self._index_echo = 0

        self._is_photo_ext = set((".jpg", ".jpeg", ".JPG", ".png"))
        self._thumb_size = 50

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
        log.info(f"Setting index_prim to '{index_prim}'")
        self._index_prim = index_prim
        self._update_photo_prim(self._active_photo_list[index_prim])

    def moveIndexPrim(self, direction):
        if direction == "forward":
            new_index_prim = self._index_prim + 1
        elif direction == "backward":
            new_index_prim = self._index_prim - 1
        self._index_prim = new_index_prim % len(self.photo_info_list_active.get())
        self._update_photo_prim(self._active_photo_list[self._index_prim])

    def seekIndexPrim(self, pic):
        self._index_prim = self._active_photo_list.index(pic)
        self._update_photo_prim(pic)

    def _update_photo_prim(self, pic):
        """Change what is needed for a new pic

        - current_photo_prim
        - cropped_prim
        """
        self.current_photo_prim.set(pic)

    def moveIndexEcho(self, direction):
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
        log.info(f"Updating photo echo, index {self._index_echo}")  # {data}")
        self.current_photo_echo.set(pic)

    def likePressed(self, which_frame):
        """Update selection_list accordingly
        """
        log = logging.getLogger(f"c.{__class__.__name__}.likePressed")
        log.setLevel("TRACE")
        log.info(f"Like pressed on {which_frame}")

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


class ModelCrop:
    def __init__(self):
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")
