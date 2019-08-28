import logging
import tkinter as tk

from os.path import basename

from label_pixel import LabelPixel
from scrollable_frame import ScrollableFrame
from thumb_button import ThumbButton
from color_palette import Palette


class View:
    def __init__(self, root):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info("Start init")

        self.root = root
        self.palette = Palette("blue")

        self.setup_main_window()

        # create frames for photo and info panels
        self.frame_crop_prim = FrameCrop(
            self.root, name="frame_crop_prim", palette=self.palette
        )
        self.frame_crop_echo = FrameCrop(
            self.root, name="frame_crop_echo", palette=self.palette
        )
        self.frame_metadata = FrameMetadata(
            self.root,
            sidebar_width=self.right_sidebar_width,
            name="frame_metadata",
            palette=self.palette,
        )
        self.frame_path_info = FramePathInfo(
            parent=self.root,
            sidebar_width=self.right_sidebar_width,
            name="frame_path_info",
            palette=self.palette,
        )

        # MAYBE there could in View reaction callbacks to call from the controller
        # to insulate the view even more, as the controller would call a generic
        # self.view.updatedPhotoList, and inside View.updatedPhotoList there would
        # be the actual implementation

    def setup_main_window(self):
        """Setup main window aesthetics
        """
        self.width = 900
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        icon_img = tk.PhotoImage(file="./LogoPV64_2-2.gif")
        self.root.iconphoto(True, icon_img)

        # TODO add some info in titlebar

        # setup elements dimensions
        # TODO sidebar width set using grid_rowconfigure(minwidth)
        self.right_sidebar_width = 250

    def layout_set(self, lay_num):
        logg = logging.getLogger(f"c.{__class__.__name__}.layout_set")
        logg.info(f"Setting layout {lay_num}")

        self.layout_reset()
        if lay_num == 0:
            self.layout_i()
        elif lay_num == 1:
            self.layout_ii()
        elif lay_num == 2:
            self.layout_im()
        elif lay_num == 3:
            self.layout_ip()
        elif lay_num == 4:
            self.layout_imp()

    def layout_reset(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.layout_reset")
        #  logg.setLevel("TRACE")
        logg.trace("Reset layout")

        # forget all widgets
        self.frame_crop_prim.grid_forget()
        self.frame_crop_echo.grid_forget()
        self.frame_metadata.grid_forget()
        self.frame_path_info.grid_forget()

        # reset weight for row and col
        max_row = 1
        max_col = 1
        for i in range(max_row + 1):
            self.root.grid_rowconfigure(i, weight=0, uniform="")
        for i in range(max_col + 1):
            self.root.grid_columnconfigure(i, weight=0, uniform="")

    def layout_i(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")

    def layout_im(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_metadata.grid(row=1, column=0, sticky="ew")

    def layout_ip(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_path_info.grid(row=0, column=1, sticky="nsew")

    def layout_imp(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_metadata.grid(row=1, column=0, sticky="ew")
        self.frame_path_info.grid(row=0, column=1, rowspan=2, sticky="ns")

    def layout_ii(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1, uniform="half")
        self.root.grid_columnconfigure(1, weight=1, uniform="half")
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_crop_echo.grid(row=0, column=1, sticky="nsew")

    def exit(self):
        self.root.destroy()


class FrameCrop(tk.Frame):
    def __init__(self, parent, name, palette, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.name = name
        self.palette = palette
        back_col = self.palette.get_colors(f"background.{self.name}")

        super().__init__(parent, background=back_col, *args, **kwargs)

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the label that will hold the image
        self.image_label = tk.Label(
            self, text="Mock up FrameCrop", background=self.cget("background")
        )

        # grid it, do not expand
        self.image_label.grid(row=0, column=0)
        # stop propagation of grid dim: A boolean argument specifies whether
        # the geometry information of the slaves will determine the size of
        # this widget.
        #  self.grid_propagate(False)
        # let the dimension propagate up: this triggers the configure event,
        # but the size of the columns is determined by
        # grid_columnconfigure(uniform='half')

    def update_image(self, data):
        """Update the image in the label
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_image")
        logg.trace(f"Updating image_label")
        self.image_label.configure(image=data)

    def bind_mouse_scroll_label(self, func):
        """Bind mouse scroll events *only* to image_label
        """
        self.image_label.bind("<4>", func)
        self.image_label.bind("<5>", func)
        self.image_label.bind("<MouseWheel>", func)

    def bind_mouse_scroll_frame(self, func):
        """Bind mouse scroll events *only* to image_frame
        """
        self.bind("<4>", func)
        self.bind("<5>", func)
        self.bind("<MouseWheel>", func)

    def bind_image(self, kind, func):
        """Bind event 'kind' to func *only* on image_label
        """
        self.image_label.bind(kind, func)

    def bind_to_all(self, kind, func):
        """Bind event 'kind' to func on *both* image_label and frame
        """
        self.bind(kind, func)
        self.image_label.bind(kind, func)


class FrameMetadata(tk.Frame):
    """Container class for metadata info
    """

    def __init__(self, parent, name, palette, sidebar_width, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.name = name
        self.palette = palette
        back_col = self.palette.get_colors(f"background.{self.name}")

        super().__init__(
            parent, width=sidebar_width, background=back_col, *args, **kwargs
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.temp = tk.Label(
            self, text="Mock up Metadata", background=self.cget("background")
        )
        self.temp.grid(row=0, column=0)


class MetadataFrame(tk.Frame):
    """Element class to show metadata info
    """


class TagFrame(tk.Frame):
    """Element to add tags to the image

    Possibly in the tag exif field
    """


class FramePathInfo(tk.Frame):
    """Container class for input/output folder, photo/selection list
    """

    def __init__(self, parent, name, palette, sidebar_width, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info("Start init")
        logg.trace(f"args {args}")
        logg.trace(f"kwargs {kwargs}")

        self.name = name
        self.palette = palette
        back_col = self.palette.get_colors(f"background.{self.name}")

        super().__init__(
            parent, width=sidebar_width, background=back_col, *args, **kwargs
        )

        # save dimensions of elements
        self.sidebar_width = sidebar_width

        # CREATE children frames
        logg.trace(f"self.sidebar_width {self.sidebar_width}")
        self.output_frame = OutputFrame(self, name="output_frame", palette=self.palette)
        self.input_frame = InputFrame(self, name="input_frame", palette=self.palette)
        self.selection_list_frame = SelectionListFrame(
            self,
            width=self.sidebar_width,
            name="photo_list_frame",
            palette=self.palette,
            sidebar_width=self.sidebar_width,
        )
        self.photo_list_frame = PhotoListFrame(
            self,
            width=self.sidebar_width,
            name="photo_list_frame",
            palette=self.palette,
            sidebar_width=self.sidebar_width,
        )

        # setup grid for FramePathInfo
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # GRID childrens
        self.output_frame.grid(row=0, column=0, sticky="ew")
        self.input_frame.grid(row=1, column=0, sticky="ew")
        self.selection_list_frame.grid(row=2, column=0, sticky="nsew")
        self.photo_list_frame.grid(row=3, column=0, sticky="nsew")


class OutputFrame(tk.Frame):
    def __init__(self, parent, name, palette, *args, **kwargs):
        """Do things in build_output_frame
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.name = name
        self.palette = palette

        # frame background color
        self.back_col = self.palette.get_colors(f"background.{self.name}")

        # header background color
        self.back_col_header = (
            self.palette.get_colors(f"background.output_frame_header"),
        )

        # set folder button
        self.back_col_output_setfolder = self.palette.get_colors(
            f"background.output_setfolder"
        )
        self.hover_col_output_setfolder = self.palette.get_colors(
            f"hover.output_setfolder"
        )

        # set folder label
        self.back_col_output_label = self.palette.get_colors(f"background.output_label")

        super().__init__(parent, background=self.back_col, *args, **kwargs)

        self.output_frame_header = tk.Label(
            self, text="Output folder:", background=self.back_col_header
        )

        self.btn_set_output_folder = tk.Button(
            self,
            text="Set output folder",
            borderwidth=0,
            background=self.back_col_output_setfolder,
            activebackground=self.hover_col_output_setfolder,
            highlightthickness=0,
        )
        self.output_folder_var = tk.StringVar(value="Not set")

        self.text_output_folder = tk.Label(
            self,
            textvariable=self.output_folder_var,
            background=self.back_col_output_label,
        )

        # grid the elements, grow only the label
        self.grid_columnconfigure(0, weight=1)

        self.output_frame_header.grid(row=0, column=0, sticky="ew")
        self.text_output_folder.grid(row=1, column=0, sticky="ew")
        self.btn_set_output_folder.grid(row=2, column=0)

    def update_output_frame(self, output_folder_full):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_output_frame")
        logg.info("Updating label output_folder")
        # MAYBE showing a right aligned full path might be more informative
        self.output_folder_var.set(basename(output_folder_full))


class InputFrame(tk.Frame):
    def __init__(self, parent, name, palette, *args, **kwargs):
        """Do things in build_input_frame
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.name = name
        self.palette = palette

        # frame background color
        self.back_col = self.palette.get_colors(f"background.{self.name}")

        # header background color
        self.back_col_header = (
            self.palette.get_colors(f"background.input_frame_header"),
        )

        # add folder button
        self.back_col_input_addfolder = self.palette.get_colors(
            f"background.input_addfolder"
        )
        self.hover_col_input_addfolder = self.palette.get_colors(
            f"hover.input_addfolder"
        )

        # checkbuttons
        self.back_col_input_chkbtn = self.palette.get_colors(f"background.input_chkbtn")
        self.hover_col_input_chkbtn = self.palette.get_colors(f"hover.input_chkbtn")
        self.select_col_input_chkbtn = self.palette.get_colors(f"select.input_chkbtn")

        super().__init__(parent, background=self.back_col, *args, **kwargs)

        self.input_frame_header = tk.Label(
            self, text="Input folder:", background=self.back_col_header
        )

        # create static elements
        self.btn_add_folder = tk.Button(
            self,
            text="Add input folder",
            borderwidth=0,
            background=self.back_col_input_addfolder,
            activebackground=self.hover_col_input_addfolder,
            highlightthickness=0,
        )

        # setup grid in input_frame
        self.grid_columnconfigure(0, weight=1)

        # grid static elements
        self.input_frame_header.grid(row=0, column=0, sticky="ew")
        self.btn_add_folder.grid(row=1, column=0)

        # dicts for runtime elements
        self.checkbtn_input_fold = {}
        self.checkbtn_input_state = {}

    def update_input_frame(self, input_folders):
        """Draw the selected input_folders

        input_folders is a dict of { path : state }
        When a new folder is added, create the corresponding Checkbutton,
        then repack them all
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_input_frame")
        logg.info("Updating input_folder checkbuttons")

        for ri, folder in enumerate(sorted(input_folders)):
            folder_name = basename(folder)

            # create the Checkbutton for the new folder
            if not folder in self.checkbtn_input_fold:
                self.checkbtn_input_state[folder] = tk.BooleanVar(value=True)
                self.checkbtn_input_fold[folder] = tk.Checkbutton(
                    self,
                    text=folder_name,
                    background=self.back_col_input_chkbtn,
                    variable=self.checkbtn_input_state[folder],
                    command=self.generate_virtual_toggling_input_folder,
                    highlightthickness=0,
                    activebackground=self.hover_col_input_chkbtn,
                    selectcolor=self.select_col_input_chkbtn,
                    borderwidth=0,
                )

            # grid the Checkbutton
            self.checkbtn_input_fold[folder].grid(row=ri + 2, column=0, sticky="ew")
            # copy the state from what you receive from the model
            self.checkbtn_input_state[folder].set(input_folders[folder])

    def generate_virtual_toggling_input_folder(self):
        """Generate a virtual event to notify the controller of a toggled Checkbutton
        """
        self.event_generate("<<toggle_input_folder>>")


class ThumbButtonList(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def on_thumbbtn_enter(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_thumbbtn_enter")
        #  logg.setLevel("TRACE")
        logg.trace("Enter ThumbButton")
        logg.trace(f"Event {event} fired by {event.widget}")
        event.widget.on_enter()

    def on_thumbbtn_leave(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_thumbbtn_leave")
        #  logg.setLevel("TRACE")
        logg.trace("Leave ThumbButton")
        logg.trace(f"Event {event} fired by {event.widget}")
        event.widget.on_leave()


class SelectionListFrame(ThumbButtonList):
    def __init__(self, parent, name, palette, sidebar_width, *args, **kwargs):
        """Do things in build_selection_list_frame
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.name = name
        self.palette = palette
        self.sidebar_width = sidebar_width

        # frame background color
        self.back_col = self.palette.get_colors(f"background.{self.name}")

        # header background color
        self.back_col_header = (
            self.palette.get_colors(f"background.selection_list_frame_header"),
        )

        # ScrollableFrame colors
        self.back_col_scrollable = self.palette.get_colors(
            f"background.selection_list_scrollable"
        )
        self.hover_col_scrollable = self.palette.get_colors(
            f"hover.selection_list_scrollable"
        )
        self.slider_col_scrollable = self.palette.get_colors(
            f"slider.selection_list_scrollable"
        )

        # ThumbButton colors
        self.back_col_thumbbtn = self.palette.get_colors(
            f"background.selection_list_thumbbtn"
        )
        self.hover_back_col_thumbbtn = self.palette.get_colors(
            f"hover.selection_list_thumbbtn"
        )
        self.back_col_bis_thumbbtn = self.palette.get_colors(
            f"backgroundbis.selection_list_thumbbtn"
        )

        super().__init__(parent, background=self.back_col, *args, **kwargs)

        self.selection_list_frame_header = tk.Label(
            self, text="Selection list:", background=self.back_col_header
        )

        # ScrollableFrame that holds the ThumbButtons
        self.selection_list_scrollable = ScrollableFrame(
            self,
            scroll_width=self.sidebar_width,
            back_col=self.back_col_scrollable,
            hover_back_col=self.hover_col_scrollable,
            slider_col=self.slider_col_scrollable,
        )

        # setup grid in selection_list_frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # grid static elements
        self.selection_list_frame_header.grid(row=0, column=0, sticky="ew")
        self.selection_list_scrollable.grid(row=1, column=0, sticky="nsew")

        # dicts for runtime elements
        self.selection_list_thumbbtn = {}

    def update_selection_list(self, selection_list_info):
        """Receives a dict of PhotoInfo object and creates ThumbButton

        There is also info on whether the pic is still selected
        selection_list_info = { pic : (PhotoInfo, is_selected) }
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_selection_list")
        #  logg.setLevel("TRACE")
        logg.info(f"Updating selection_list ThumbButtons")

        for pic in self.selection_list_thumbbtn:
            self.selection_list_thumbbtn[pic].grid_forget()

        for ri, pic in enumerate(selection_list_info):
            # extract values
            photo_info = selection_list_info[pic][0]
            is_selected = selection_list_info[pic][1]

            # create the new ThumbButton
            if not pic in self.selection_list_thumbbtn:
                self.selection_list_thumbbtn[pic] = ThumbButton(
                    self.selection_list_scrollable.scroll_frame,
                    photo_info,
                    back_col=self.back_col_thumbbtn,
                    hover_back_col=self.hover_back_col_thumbbtn,
                    back_col_bis=self.back_col_bis_thumbbtn,
                )

                # bind enter/leave event to highlight
                self.selection_list_thumbbtn[pic].bind(
                    "<Enter>", self.on_thumbbtn_enter
                )
                self.selection_list_thumbbtn[pic].bind(
                    "<Leave>", self.on_thumbbtn_leave
                )

                # bind scroll function to ThumbButton elements
                self.selection_list_thumbbtn[pic].register_scroll_func(
                    self.selection_list_scrollable.on_list_scroll
                )

                # add event for doubleclick
                self.selection_list_thumbbtn[pic].bind_doubleclick(
                    self.on_selection_list_doubleclick
                )

            # set selected photo to FIRST, de-selected to BIS color_mode
            if is_selected:
                self.selection_list_thumbbtn[pic].set_back_col_mode("FIRST")
            else:
                self.selection_list_thumbbtn[pic].set_back_col_mode("BIS")

            self.selection_list_thumbbtn[pic].grid(row=ri, column=0, sticky="ew")

    def on_selection_list_doubleclick(self, event):
        logg = logging.getLogger(
            f"c.{__class__.__name__}.on_selection_list_doubleclick"
        )
        #  logg.setLevel("TRACE")
        logg.debug("Doublecliked something in selection list")
        logg.trace(
            f"Event {event} fired by {event.widget} master {event.widget.master}"
        )
        self.selection_doubleclicked = event.widget.master.photo_info.photo_name_full
        logg.trace(f"selection_doubleclicked {self.selection_doubleclicked}")
        self.event_generate("<<thumbbtn_selection_doubleclick>>")


class PhotoListFrame(ThumbButtonList):
    def __init__(self, parent, name, palette, sidebar_width, *args, **kwargs):
        """Do things in build_photo_list_frame
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.name = name
        self.palette = palette

        self.back_col = self.palette.get_colors(f"background.{self.name}")

        self.back_col_header = (
            self.palette.get_colors(f"background.photo_list_frame_header"),
        )

        self.back_col_scrollable = self.palette.get_colors(
            f"background.photo_list_scrollable"
        )
        self.hover_col_scrollable = self.palette.get_colors(
            f"hover.photo_list_scrollable"
        )
        self.slider_col_scrollable = self.palette.get_colors(
            f"slider.photo_list_scrollable"
        )

        self.back_col_thumbbtn = self.palette.get_colors(
            f"background.photo_list_thumbbtn"
        )
        self.hover_back_col_thumbbtn = self.palette.get_colors(
            f"hover.photo_list_thumbbtn"
        )
        self.back_col_bis_thumbbtn = self.palette.get_colors(
            f"backgroundbis.photo_list_thumbbtn"
        )

        super().__init__(parent, background=self.back_col, *args, **kwargs)

        # save width of sidebar, needed to explicitly set ScrollableFrame
        self.sidebar_width = sidebar_width

        self.photo_list_frame_header = tk.Label(
            self, text="Photo list:", background=self.back_col_header
        )

        # TODO reimplement the whole thing: manually change the TB you show
        # ask for new PhotoInfo when needed, so that they do not have to be all
        # loaded; bind configure of photo_list_frame to compute how many TB
        # have to be available; bind scroll (from the Scrollbar as well?) to a
        # call in the model to update the list of TB, and show just them
        # this is mainly needed because this frame can only hold a puny 1000ish
        # photo list; that's like one week of vacation.

        # ScrollableFrame that holds the ThumbButtons
        self.photo_list_scrollable = ScrollableFrame(
            self,
            scroll_width=self.sidebar_width,
            back_col=self.back_col_scrollable,
            hover_back_col=self.hover_col_scrollable,
            slider_col=self.slider_col_scrollable,
        )

        # setup grid in photo_list_frame (this widget)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # grid static elements
        self.photo_list_frame_header.grid(row=0, column=0, sticky="ew")
        self.photo_list_scrollable.grid(row=1, column=0, sticky="nsew")

        # dicts for runtime elements
        self.photo_list_thumbbtn = {}
        self.current_photo_prim = ""

    def update_photo_list(self, photo_list_info):
        """Receives a dict of PhotoInfo object and creates ThumbButton

        photo_list_info = { pic : PhotoInfo }
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_photo_list")
        logg.setLevel("TRACE")
        logg.info("Updating photo_list ThumbButton")

        for pic in self.photo_list_thumbbtn:
            self.photo_list_thumbbtn[pic].grid_forget()

        for ri, pic in enumerate(photo_list_info):
            # create the new ThumbButton
            if not pic in self.photo_list_thumbbtn:
                self.photo_list_thumbbtn[pic] = ThumbButton(
                    self.photo_list_scrollable.scroll_frame,
                    photo_list_info[pic],
                    back_col=self.back_col_thumbbtn,
                    hover_back_col=self.hover_back_col_thumbbtn,
                    back_col_bis=self.back_col_bis_thumbbtn,
                )

                # bind enter/leave event to highlight
                self.photo_list_thumbbtn[pic].bind("<Enter>", self.on_thumbbtn_enter)
                self.photo_list_thumbbtn[pic].bind("<Leave>", self.on_thumbbtn_leave)

                # bind scroll function to ThumbButton elements
                self.photo_list_thumbbtn[pic].register_scroll_func(
                    self.photo_list_scrollable.on_list_scroll
                )

                # add event for doubleclick
                self.photo_list_thumbbtn[pic].bind_doubleclick(
                    self.on_photo_list_doubleclick
                )

            # highlight current photo primary
            if pic == self.current_photo_prim:
                logg.trace(f"Setting color mode BIS for '{pic}' ThumbButton")
                self.photo_list_thumbbtn[pic].set_back_col_mode("BIS")
            else:
                self.photo_list_thumbbtn[pic].set_back_col_mode("FIRST")

            # grid the ThumbButton
            self.photo_list_thumbbtn[pic].grid(row=ri, column=0, sticky="ew")

        logg.trace(f"Loaded thbtn {self.photo_list_thumbbtn.keys()}")

    def on_photo_list_doubleclick(self, event):
        """Handle double clicks on photo list, go to that pic

        MAYBE better binding of this event in ThumbButton, bind the double
        click to some virtual events raised, then bind the virtual event on the
        ThumbButton top widget, so that the callback can access event.widget
        directly on the ThumbButton, instead of event.widget.master
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.on_photo_list_doubleclick")
        #  logg.setLevel("TRACE")
        logg.debug("Doublecliked something")
        logg.trace(
            f"Event {event} fired by {event.widget} master {event.widget.master}"
        )
        self.photo_doubleclicked = event.widget.master.photo_info.photo_name_full
        logg.trace(f"photo_doubleclicked {self.photo_doubleclicked}")
        self.event_generate("<<thumbbtn_photo_doubleclick>>")

    def update_current_photo_prim(self, pic):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_current_photo_prim")
        #  logg.setLevel("TRACE")
        logg.trace("Update current_photo_prim")
        if self.current_photo_prim != "":
            self.photo_list_thumbbtn[self.current_photo_prim].set_back_col_mode("FIRST")
        self.photo_list_thumbbtn[pic].set_back_col_mode("BIS")
        self.current_photo_prim = pic
