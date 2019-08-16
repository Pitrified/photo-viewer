import logging
import tkinter as tk

from os.path import basename
from PIL import ImageTk, Image

from label_pixel import LabelPixel


class ThumbButton(tk.Frame):
    def __init__(self, parent, photo_info, back_col, active_back_col, *args, **kwargs):
        super().__init__(parent, background=back_col, *args, **kwargs)

        self.photo_info = photo_info

        # setup grid
        self.grid_rowconfigure(0, weight=1, minsize=30)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # create child widgets

        # thumbnail
        self.thumb_label = tk.Label(
            self,
            width=self.photo_info.thumb_size,
            bg=back_col,
            activebackground=active_back_col,
        )
        tkimg = ImageTk.PhotoImage(self.photo_info.thumb)
        self.thumb_label.image = tkimg
        self.thumb_label.configure(image=tkimg)

        # photo name, width set in pixel
        #  self.photo_text = LabelPixel(
        #  self, text=basename(self.photo_info.photo_name_full)
        #  )
        self.photo_text = tk.Label(
            self,
            text=basename(self.photo_info.photo_name_full),
            bg=back_col,
            activebackground=active_back_col,
        )

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
