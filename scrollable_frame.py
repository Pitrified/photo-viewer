import logging

import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, scroll_width, back_col, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.scroll_width = scroll_width

        # create scrollbar for canvas
        self.scroll_bar = tk.Scrollbar(self)

        # create the canvas and bind it to Scrollbar
        self.scroll_canvas = tk.Canvas(
            self,
            bg=back_col,
            yscrollcommand=self.scroll_bar.set,
            width=self.scroll_width - 13,
            highlightthickness=0,
        )

        # bind Scrollbar to Canvas
        self.scroll_bar.config(command=self.scroll_canvas.yview)

        # create the Frame to put inside the Canvas
        # thanks to the wizard BO https://stackoverflow.com/a/3092341
        self.scroll_frame = tk.Frame(
            self.scroll_canvas, bg=back_col, width=self.scroll_width - 13
        )

        # setup grid for Scrollbar and Canvas
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        # and grid them
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_bar.grid(row=0, column=1, sticky="ns")

        # place the Frame on the Canvas
        self.scroll_canvas.create_window(
            (0, 0),
            window=self.scroll_frame,
            anchor="nw",
            tags="self.scroll_frame",
            width=self.scroll_width - 13,
        )

        # bind resizing of canvas scrollregion
        self.scroll_frame.bind("<Configure>", self.on_scroll_frame_configure)

        # setup grid for internal frame
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # bind scroll to empty canvas
        self.scroll_canvas.bind("<4>", self.on_list_scroll)
        self.scroll_canvas.bind("<5>", self.on_list_scroll)
        self.scroll_canvas.bind("<MouseWheel>", self.on_list_scroll)

    def on_scroll_frame_configure(self, e):
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def on_list_scroll(self, e):
        log = logging.getLogger(f"c.{__class__.__name__}.on_list_scroll")
        if e.num == 4 or e.delta == 120 or e.delta == 1:
            number = -1
        elif e.num == 5 or e.delta == -120 or e.delta == -1:
            number = 1
        else:
            log.error(f"Errors when scrolling {e}")

        log.trace(f"Scrolling list {number} units, event {e} from {e.widget}")
        self.scroll_canvas.yview_scroll(number, "units")
