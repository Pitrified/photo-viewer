import logging
import tkinter as tk

from os.path import basename

from label_pixel import LabelPixel


class View:
    def __init__(self, root):
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        self.root = root

        self.setup_main_window()

        # create frames for photo and info panels
        self.frame_crop_prim = FrameCrop(self.root, bg="SeaGreen1")
        self.frame_crop_echo = FrameCrop(self.root, bg="SeaGreen3")
        self.frame_metadata = FrameMetadata(
            self.root, width=self.right_sidebar_width, bg="SpringGreen2"
        )
        self.frame_path_info = FramePathInfo(
            self.root, width=self.right_sidebar_width, bg="DarkGoldenrod1"
        )

        self.layout_setup()

    def setup_main_window(self):
        """Setup main window aesthetics
        """
        self.width = 900
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        icon_img = tk.PhotoImage(file="./LogoPV64_2-2.gif")
        self.root.iconphoto(True, icon_img)

        # setup elements dimensions
        self.right_sidebar_width = 250

    def layout_setup(self):
        # setup layout info
        self.layout_tot = 5
        self.layout_is_double = (1,)
        # set starting layout
        self.layout_current = 4
        self.layout_set(self.layout_current)

    def layout_set(self, lay_num):
        log = logging.getLogger(f"c.{__class__.__name__}.l_set")
        log.debug(f"Setting layout {lay_num}")

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

    def layout_cycle(self):
        log = logging.getLogger(f"c.{__class__.__name__}.l_cycle")
        #  log.setLevel("TRACE")
        log.trace("Cycling layout")

        self.layout_current = (self.layout_current + 1) % self.layout_tot
        self.layout_set(self.layout_current)

    def layout_reset(self):
        log = logging.getLogger(f"c.{__class__.__name__}.l_reset")
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
            self.root.grid_rowconfigure(i, weight=0)
        for i in range(max_col + 1):
            self.root.grid_columnconfigure(i, weight=0)

    def layout_i(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")

    def layout_im(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_metadata.grid(row=0, column=1, sticky="ns")

    def layout_ip(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_path_info.grid(row=0, column=1, sticky="nsew")

    def layout_imp(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.frame_metadata.grid(row=0, column=1, sticky="nsew")
        self.frame_path_info.grid(row=1, column=1, sticky="nsew")

    def layout_ii(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.frame_crop_prim.grid(row=0, column=0, sticky="nsew")
        self.frame_crop_echo.grid(row=0, column=1, sticky="nsew")

    def exit(self):
        self.root.destroy()


class FrameCrop(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FrameMetadata(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class FramePathInfo(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        # CREATE children frames
        cur_width = self.winfo_width()
        self.output_frame = tk.Frame(self, width=cur_width, bg="SkyBlue1")
        self.input_frame = tk.Frame(self, width=cur_width, bg="SkyBlue2")
        self.selection_list_frame = tk.Frame(self, width=cur_width, bg="SkyBlue3")
        self.photo_list_frame = tk.Frame(self, width=cur_width, bg="SkyBlue4")

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

    def build_output_frame(self):
        self.btn_set_output_folder = tk.Button(
            self.output_frame, text="Set output folder"
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
        self.btn_add_folder = tk.Button(self.input_frame, text="Add directory to list")
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
        log.info("Building photo_list_frame")
        cur_width = self.winfo_width()
        # static elements
        self.photo_list_frame_header = LabelPixel(
            self, width=cur_width, text="Photo list:"
        )
        self.photo_list_frame_header.grid(row=0, column=0)
