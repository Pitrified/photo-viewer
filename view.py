import logging
import tkinter as tk

from os.path import basename

from label_pixel import LabelPixel
from scrollable_frame import ScrollableFrame
from thumb_button import ThumbButton


class View:
    def __init__(self, root):
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        self.root = root

        self.setup_main_window()

        # create frames for photo and info panels
        self.frame_crop_prim = FrameCrop(self.root, back_col="SeaGreen1")
        self.frame_crop_echo = FrameCrop(self.root, back_col="SeaGreen3")
        self.frame_metadata = FrameMetadata(
            self.root, sidebar_width=self.right_sidebar_width, bg="SpringGreen2"
        )
        self.frame_path_info = FramePathInfo(
            parent=self.root,
            sidebar_width=self.right_sidebar_width,
            bg="DarkGoldenrod1",
        )

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
        self.right_sidebar_width = 250

    def layout_set(self, lay_num):
        log = logging.getLogger(f"c.{__class__.__name__}.layout_set")
        log.info(f"Setting layout {lay_num}")

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
        log = logging.getLogger(f"c.{__class__.__name__}.layout_reset")
        #  log.setLevel("TRACE")
        log.trace("Reset layout")

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
    def __init__(self, parent, back_col, *args, **kwargs):
        super().__init__(parent, background=back_col, *args, **kwargs)
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info(f"Start init")

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
        self.grid_propagate(False)

    def update_image(self, data):
        """Update the image in the label
        """
        log = logging.getLogger(f"c.{__class__.__name__}.update_image")
        log.trace(f"Updating image_label")
        self.image_label.configure(image=data)

    def bind_mouse_scroll_label(self, func):
        """Bind mouse events to image_label
        """
        self.image_label.bind("<4>", func)
        self.image_label.bind("<5>", func)
        self.image_label.bind("<MouseWheel>", func)

    def bind_mouse_scroll_frame(self, func):
        """Bind mouse events to image_frame
        """
        self.bind("<4>", func)
        self.bind("<5>", func)
        self.bind("<MouseWheel>", func)

    def bind_image(self, kind, func):
        """Bind event 'kind' to func on image_label
        """
        self.image_label.bind(kind, func)


class FrameMetadata(tk.Frame):
    def __init__(self, parent, sidebar_width, *args, **kwargs):
        super().__init__(parent, width=sidebar_width, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.temp = tk.Label(
            self, text="Mock up Metadata", background=self.cget("background")
        )
        self.temp.grid(row=0, column=0)


class FramePathInfo(tk.Frame):
    def __init__(self, parent, sidebar_width, *args, **kwargs):
        super().__init__(parent, width=sidebar_width, *args, **kwargs)

        log = logging.getLogger(f"c.{__class__.__name__}.init")
        #  log.setLevel("TRACE")
        log.info("Start init")
        log.trace(f"args {args}")
        log.trace(f"kwargs {kwargs}")

        # save dimensions of elements
        self.sidebar_width = sidebar_width

        # CREATE children frames
        log.trace(f"self.sidebar_width {self.sidebar_width}")
        self.output_frame = tk.Frame(self, width=self.sidebar_width, bg="SkyBlue1")
        self.input_frame = tk.Frame(self, width=self.sidebar_width, bg="SkyBlue2")
        self.selection_list_frame = tk.Frame(
            self, width=self.sidebar_width, bg="SkyBlue3"
        )
        self.photo_list_frame = tk.Frame(self, width=self.sidebar_width, bg="SkyBlue4")

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

        self.build_output_frame()
        self.build_input_frame()
        self.build_photo_list_frame()
        self.build_selection_list_frame()

    def build_output_frame(self):
        self.btn_set_output_folder = tk.Button(
            self.output_frame,
            text="Set output folder",
            borderwidth=0,
            background="SkyBlue2",
            activebackground="LightSkyBlue2",
            highlightthickness=0,
        )
        self.output_folder_var = tk.StringVar(value="Not set not seen")
        self.text_output_folder = tk.Label(
            self.output_frame,
            textvariable=self.output_folder_var,
            background=self.output_frame.cget("background"),
        )

        # grid the elements, grow only the label
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.btn_set_output_folder.grid(row=0, column=0)
        self.text_output_folder.grid(row=1, column=0, sticky="ew")

    def update_output_frame(self, output_folder_full):
        log = logging.getLogger(f"c.{__class__.__name__}.update_output_frame")
        log.info("Updating label output_folder")
        # MAYBE showing a right aligned full path might be more informative
        self.output_folder_var.set(basename(output_folder_full))

    def build_input_frame(self):
        # create static elements
        self.btn_add_folder = tk.Button(
            self.input_frame,
            text="Add directory to list",
            borderwidth=0,
            background="SkyBlue3",
            activebackground="LightSkyBlue3",
            highlightthickness=0,
        )
        # setup grid in input_frame
        self.input_frame.grid_columnconfigure(0, weight=1)
        # grid static elements
        self.btn_add_folder.grid(row=0, column=0)
        # dicts for runtime elements
        self.checkbtn_input_fold = {}
        self.checkbtn_input_state = {}

    def update_input_frame(self, input_folders):
        """Draw the selected input_folders

        input_folders is a dict of { path : state }
        When a new folder is added, create the corresponding Checkbutton,
        then repack them all
        """
        log = logging.getLogger(f"c.{__class__.__name__}.update_input_frame")
        log.info("Updating input_folder checkbuttons")

        for ri, folder in enumerate(sorted(input_folders)):
            folder_name = basename(folder)

            # create the Checkbutton for the new folder
            if not folder in self.checkbtn_input_fold:
                self.checkbtn_input_state[folder] = tk.BooleanVar(value=True)
                self.checkbtn_input_fold[folder] = tk.Checkbutton(
                    self.input_frame,
                    text=folder_name,
                    background=self.input_frame.cget("background"),
                    variable=self.checkbtn_input_state[folder],
                    command=self.generate_virtual_toggling_input_folder,
                    highlightthickness=0,
                    activebackground="SkyBlue1",
                    selectcolor="SkyBlue1",
                    borderwidth=0,
                )

            # grid the Checkbutton
            self.checkbtn_input_fold[folder].grid(row=ri + 1, column=0, sticky="ew")
            # copy the state from what you receive from the model
            self.checkbtn_input_state[folder].set(input_folders[folder])

    def generate_virtual_toggling_input_folder(self):
        """Generate a virtual event to notify the controller of a toggled Checkbutton
        """
        self.input_frame.event_generate("<<toggle_input_folder>>")

    def build_photo_list_frame(self):
        log = logging.getLogger(f"c.{__class__.__name__}.build_photo_list_frame")
        #  log.setLevel("TRACE")
        log.info("Building photo_list_frame")
        log.trace(f"self.sidebar_width {self.sidebar_width}")

        # STATIC elements

        self.photo_list_frame_header = tk.Label(
            self.photo_list_frame,
            text="Photo list:",
            background=self.photo_list_frame.cget("background"),
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
            self.photo_list_frame,
            scroll_width=self.sidebar_width,
            back_col=self.photo_list_frame.cget("background"),
            hover_back_col="SkyBlue2",
            slider_col="DeepSkyBlue4",
        )

        # setup grid in photo_list_frame
        self.photo_list_frame.grid_rowconfigure(1, weight=1)
        self.photo_list_frame.grid_columnconfigure(0, weight=1)

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
        log = logging.getLogger(f"c.{__class__.__name__}.update_photo_list")
        #  log.setLevel("TRACE")
        log.info("Updating photo_list ThumbButton")

        for pic in self.photo_list_thumbbtn:
            self.photo_list_thumbbtn[pic].grid_forget()

        for ri, pic in enumerate(photo_list_info):
            # create the new ThumbButton
            if not pic in self.photo_list_thumbbtn:
                self.photo_list_thumbbtn[pic] = ThumbButton(
                    self.photo_list_scrollable.scroll_frame,
                    photo_list_info[pic],
                    back_col=self.photo_list_frame.cget("background"),
                    hover_back_col="SkyBlue2",
                    back_col_bis="DeepSkyBlue2",
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
                log.trace(f"Setting color mode BIS for '{pic}' ThumbButton")
                self.photo_list_thumbbtn[pic].set_back_col_mode("BIS")
            else:
                self.photo_list_thumbbtn[pic].set_back_col_mode("FIRST")

            # grid the ThumbButton
            self.photo_list_thumbbtn[pic].grid(row=ri, column=0, sticky="ew")

    def on_photo_list_doubleclick(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.on_photo_list_doubleclick")
        #  log.setLevel("TRACE")
        log.debug("Doublecliked something")
        log.trace(f"Event {event} fired by {event.widget} master {event.widget.master}")
        self.photo_doubleclicked = event.widget.master.photo_info.photo_name_full
        log.trace(f"photo_doubleclicked {self.photo_doubleclicked}")
        self.photo_list_frame.event_generate("<<thumbbtn_photo_doubleclick>>")

    def update_current_photo_prim(self, pic):
        log = logging.getLogger(f"c.{__class__.__name__}.update_current_photo_prim")
        log.setLevel("TRACE")
        log.trace("Update current_photo_prim")
        if self.current_photo_prim != "":
            self.photo_list_thumbbtn[self.current_photo_prim].set_back_col_mode("FIRST")
        self.photo_list_thumbbtn[pic].set_back_col_mode("BIS")
        self.current_photo_prim = pic

    def build_selection_list_frame(self):
        log = logging.getLogger(f"c.{__class__.__name__}.build_selection_list_frame")
        #  log.setLevel("TRACE")
        log.info("Building selection_list_frame")
        log.trace(f"self.sidebar_width {self.sidebar_width}")

        # selection list header, no need for precise pixel dimensions
        self.selection_list_frame_header = tk.Label(
            self.selection_list_frame,
            text="Selection list:",
            background=self.selection_list_frame.cget("background"),
        )

        # ScrollableFrame that holds the ThumbButtons
        self.selection_list_scrollable = ScrollableFrame(
            self.selection_list_frame,
            scroll_width=self.sidebar_width,
            back_col=self.selection_list_frame.cget("background"),
            hover_back_col="SkyBlue2",
            slider_col="DeepSkyBlue3",
        )

        # setup grid in selection_list_frame
        self.selection_list_frame.grid_rowconfigure(1, weight=1)
        self.selection_list_frame.grid_columnconfigure(0, weight=1)

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
        log = logging.getLogger(f"c.{__class__.__name__}.update_selection_list")
        #  log.setLevel("TRACE")
        log.info(f"Updating selection_list ThumbButtons")

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
                    back_col=self.selection_list_frame.cget("background"),
                    hover_back_col="SkyBlue2",
                    back_col_bis="sienna2",
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
        log = logging.getLogger(f"c.{__class__.__name__}.on_selection_list_doubleclick")
        #  log.setLevel("TRACE")
        log.debug("Doublecliked something in selection list")
        log.trace(f"Event {event} fired by {event.widget} master {event.widget.master}")
        self.selection_doubleclicked = event.widget.master.photo_info.photo_name_full
        log.trace(f"selection_doubleclicked {self.selection_doubleclicked}")
        self.photo_list_frame.event_generate("<<thumbbtn_selection_doubleclick>>")

    def on_thumbbtn_enter(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.on_thumbbtn_enter")
        #  log.setLevel("TRACE")
        log.trace("Enter ThumbButton")
        log.trace(f"Event {event} fired by {event.widget}")
        event.widget.on_enter()

    def on_thumbbtn_leave(self, event):
        log = logging.getLogger(f"c.{__class__.__name__}.on_thumbbtn_leave")
        #  log.setLevel("TRACE")
        log.trace("Leave ThumbButton")
        log.trace(f"Event {event} fired by {event.widget}")
        event.widget.on_leave()
