import logging

import tkinter as tk


class View:
    def __init__(self, root):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.root = root

        # setup main window aesthetics
        self.width = 900
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        icon_img = tk.PhotoImage(file="./LogoPV64_2-2.gif")
        self.root.iconphoto(True, icon_img)

        # setup elements dimensions
        self.right_sidebar_width = 100

        # create frames for photo and info panels
        self.frame_crop_prim = FrameCrop(self.root, bg="SeaGreen1")
        self.frame_crop_echo = FrameCrop(self.root, bg="SeaGreen3")
        self.frame_metadata = FrameMetadata(
            self.root, width=self.right_sidebar_width, bg="SpringGreen2"
        )
        self.frame_path_info = FramePathInfo(
            self.root, width=self.right_sidebar_width, bg="DarkGoldenrod1"
        )

        # setup layout info
        self.layout_tot = 5
        self.layout_is_double = (1,)
        # set starting layout
        self.layout_current = 0
        self.layout_set(self.layout_current)

    def layout_set(self, lay_num):
        log = logging.getLogger(f"c.{__name__}.l_set")
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
        log = logging.getLogger(f"c.{__name__}.l_cycle")
        #  log.setLevel("TRACE")
        log.log(5, "Cycling layout")

        self.layout_current = (self.layout_current + 1) % self.layout_tot
        self.layout_set(self.layout_current)

    def layout_reset(self):
        log = logging.getLogger(f"c.{__name__}.l_reset")
        #  log.setLevel("TRACE")
        log.log(5, "Reset layout")

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
