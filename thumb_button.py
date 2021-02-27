from os.path import basename
import logging

from PIL import ImageTk  # type: ignore
import tkinter as tk


class ThumbButton(tk.Frame):
    def __init__(
        self,
        parent,
        photo_info,
        back_col,
        hover_back_col,
        back_col_bis,
        hover_back_col_bis="hover_back_col",
        *args,
        **kwargs,
    ):
        super().__init__(parent, background=back_col, *args, **kwargs)

        self.photo_info = photo_info
        self.back_col = back_col
        self.hover_back_col = hover_back_col
        self.back_col_bis = back_col_bis
        if hover_back_col_bis == "hover_back_col":
            self.hover_back_col_bis = hover_back_col
        else:
            self.hover_back_col_bis = hover_back_col_bis

        # setup grid
        self.grid_rowconfigure(0, weight=1, minsize=30)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # create child widgets

        # thumbnail
        self.thumb_label = tk.Label(
            self,
            width=self.photo_info.thumb_size,
            background=self.back_col,
            activebackground=self.hover_back_col,
        )
        tkimg = ImageTk.PhotoImage(self.photo_info.thumb)
        self.thumb_label.image = tkimg
        self.thumb_label.configure(image=tkimg)

        # photo name
        self.photo_text = tk.Label(
            self,
            text=basename(self.photo_info.photo_name_full),
            background=self.back_col,
            activebackground=self.hover_back_col,
        )

        # grid them, let both fill vertically
        self.thumb_label.grid(row=0, column=0, sticky="ns")
        self.photo_text.grid(row=0, column=1, sticky="nsew")

    def on_enter(self):
        log = logging.getLogger(f"c.{__class__.__name__}.on_enter")
        #  log.setLevel("TRACE")
        log.trace("Enter ThumbButton")

        self.thumb_label.config(state=tk.ACTIVE)
        self.photo_text.config(state=tk.ACTIVE)

    def on_leave(self):
        log = logging.getLogger(f"c.{__class__.__name__}.on_leave")
        #  log.setLevel("TRACE")
        log.trace("Leave ThumbButton")

        self.thumb_label.config(state=tk.NORMAL)
        self.photo_text.config(state=tk.NORMAL)

    def set_back_col_mode(self, color_mode):
        log = logging.getLogger(f"c.{__class__.__name__}.set_back_col_mode")
        log.setLevel("TRACE")

        if color_mode == "BIS":
            self.thumb_label.config(background=self.back_col_bis)
            self.photo_text.config(background=self.back_col_bis)
            self.thumb_label.config(activebackground=self.hover_back_col_bis)
            self.photo_text.config(activebackground=self.hover_back_col_bis)
        elif color_mode == "FIRST":
            self.thumb_label.config(background=self.back_col)
            self.photo_text.config(background=self.back_col)
            self.thumb_label.config(activebackground=self.hover_back_col)
            self.photo_text.config(activebackground=self.hover_back_col)
        else:
            log.error("Unrecognized color mode {color_mode}")

    def register_scroll_func(self, func):
        log = logging.getLogger(f"c.{__class__.__name__}.register_scroll_func")
        #  log.setLevel("TRACE")
        log.trace("Register scroll function")

        self.thumb_label.bind("<4>", func)
        self.thumb_label.bind("<5>", func)
        self.thumb_label.bind("<MouseWheel>", func)
        self.photo_text.bind("<4>", func)
        self.photo_text.bind("<5>", func)
        self.photo_text.bind("<MouseWheel>", func)

    def bind_doubleclick(self, func):
        self.thumb_label.bind("<Double-Button-1>", func)
        self.photo_text.bind("<Double-Button-1>", func)
