import logging


class Palette:
    def __init__(self, theme):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.load_theme(theme)

    def load_theme(self, theme):
        """Set the specified theme with the colors requested

        There has to be some hierarchical structure, if background.button2 is
        undefined, look for background.standard
        self.colors follows this structure:
        self.colors[background][button2]

        The clear structure is a tree, where you descend following the
        requested element, and if you don't find the key at a certain level you
        return the standard for that level, or level above.
        To do this the childrens have to know the name of the ancestors, to
        request the color with
        background.frame_path_info.photo_list_frame.photo_list_frame_header
        so the name passed should be the full ancestor list plus .childname
        The tree would look like this:
        background.standard
        background.frame_path_info
        background.frame_path_info.standard
        background.frame_path_info.photo_list_frame
        background.frame_path_info.photo_list_frame.standard
        background.frame_path_info.photo_list_frame.photo_list_frame_header
        background.frame_path_info.photo_list_frame.photo_list_scrollable
        background.frame_path_info.selection_list_frame
        background.frame_path_info.input_frame
        background.frame_path_info.output_frame

        If you don't do the tree structure, element.background is clearer

        MAYBE you can do tricks by calling theme with a color inside another,
        and then overwriting only a few items:
        if theme='dark_blue':
            self.load_theme('blue')
            color['some_element'] = 'dark_blue'
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.load_theme")
        logg.setLevel("TRACE")

        self.colors = {}
        self.colors["background"] = {}
        self.colors["backgroundbis"] = {}
        self.colors["hover"] = {}
        self.colors["hoverbis"] = {}
        self.colors["slider"] = {}
        self.colors["select"] = {}

        if theme == "badgreen":
            ###############
            # crop frames #
            ###############
            self.set_colors("background.frame_crop.prim", "SeaGreen1")
            self.set_colors("background.frame_crop.echo", "SeaGreen2")

            ##################
            # metadata frame #
            ##################
            self.set_colors("background.frame.metadata", "SeaGreen3")

            ###################
            # path info frame #
            ###################
            self.set_colors("background.frame.path_info", "SeaGreen4")

            ## output frame
            self.set_colors("background.frame.output", "SeaGreen4")
            ### output header
            self.set_colors("background.header.output", "SeaGreen3")
            ### output button set folder
            self.set_colors("background.button.output_setfolder", "SeaGreen3")
            self.set_colors("hover.button.output_setfolder", "SeaGreen2")
            ### output label
            self.set_colors("background.label.output", "SeaGreen4")

            ## input frame
            self.set_colors("background.frame.input", "SeaGreen4")
            ### input header
            self.set_colors("background.header.input", "SeaGreen3")
            ### input button add folder
            self.set_colors("background.button.input_addfolder", "SeaGreen3")
            self.set_colors("hover.button.input_addfolder", "SeaGreen2")
            ### input checkbuttons folder
            self.set_colors("background.chkbtn.input", "SeaGreen4")
            self.set_colors("hover.chkbtn.input", "SeaGreen2")
            # ... this controls the background of the check in the Checkbutton
            self.set_colors("select.chkbtn.input", "SeaGreen3")

            ## photo list frame
            self.set_colors("background.frame.photo_list", "SeaGreen4")
            ### photo list frame header
            self.set_colors("background.header.photo_list", "SeaGreen4")
            ### photo list frame ScrollableFrame
            self.set_colors("background.scrollable.photo_list", "SeaGreen4")
            self.set_colors("hover.scrollable.photo_list", "SkyBlue2")
            self.set_colors("slider.scrollable.photo_list", "DeepSkyBlue4")
            ### photo list frame ThumbButton
            self.set_colors("background.thumbbtn.photo_list", "SeaGreen4")
            self.set_colors("backgroundbis.thumbbtn.photo_list", "DeepSkyBlue2")
            self.set_colors("hover.thumbbtn.photo_list", "SkyBlue2")

            ## selection list frame
            self.set_colors("background.frame.selection_list", "SeaGreen4")
            ### selection list frame header
            self.set_colors("background.header.selection_list", "SeaGreen4")
            ### selection list frame ScrollableFrame
            self.set_colors("background.scrollable.selection_list", "SeaGreen4")
            self.set_colors("hover.scrollable.selection_list", "SkyBlue2")
            self.set_colors("slider.scrollable.selection_list", "DeepSkyBlue3")
            ### selection list frame ThumbButton
            self.set_colors("background.thumbbtn.selection_list", "SeaGreen4")
            self.set_colors("backgroundbis.thumbbtn.selection_list", "sienna2")
            self.set_colors("hover.thumbbtn.selection_list", "SkyBlue2")

        elif theme == "blue1":
            ###############
            # crop frames #
            ###############
            self.set_colors("background.frame_crop.prim", "SteelBlue1")
            self.set_colors("background.frame_crop.echo", "SteelBlue2")

            ##################
            # metadata frame #
            ##################
            self.set_colors("background.frame.metadata", "SteelBlue3")

            ###################
            # path info frame #
            ###################
            header_col = "SkyBlue4"
            back_info_col = "SkyBlue3"
            btn_col = "SkyBlue2"
            hover_col = "LightSkyBlue2"
            slider_col = "SteelBlue3"

            self.set_colors("background.frame.path_info", back_info_col)

            ## output frame
            self.set_colors("background.frame.output", back_info_col)
            ### output header
            self.set_colors("background.header.output", header_col)
            ### output button set folder
            self.set_colors("background.button.output_setfolder", btn_col)
            self.set_colors("hover.button.output_setfolder", hover_col)
            ### output label
            self.set_colors("background.label.output", back_info_col)

            ## input frame
            self.set_colors("background.frame.input", back_info_col)
            ### input header
            self.set_colors("background.header.input", header_col)
            ### input button add folder
            self.set_colors("background.button.input_addfolder", btn_col)
            self.set_colors("hover.button.input_addfolder", hover_col)
            ### input checkbuttons folder
            self.set_colors("background.chkbtn.input", back_info_col)
            self.set_colors("hover.chkbtn.input", hover_col)
            # ... this controls the background of the check in the Checkbutton
            self.set_colors("select.chkbtn.input", btn_col)

            ## photo list frame
            self.set_colors("background.frame.photo_list", back_info_col)
            ### photo list frame header
            self.set_colors("background.header.photo_list", header_col)
            ### photo list frame ScrollableFrame
            self.set_colors("background.scrollable.photo_list", back_info_col)
            self.set_colors("hover.scrollable.photo_list", hover_col)
            self.set_colors("slider.scrollable.photo_list", slider_col)
            ### photo list frame ThumbButton
            self.set_colors("background.thumbbtn.photo_list", back_info_col)
            self.set_colors("backgroundbis.thumbbtn.photo_list", "DeepSkyBlue2")
            self.set_colors("hover.thumbbtn.photo_list", hover_col)

            ## selection list frame
            self.set_colors("background.frame.selection_list", back_info_col)
            ### selection list frame header
            self.set_colors("background.header.selection_list", header_col)
            ### selection list frame ScrollableFrame
            self.set_colors("background.scrollable.selection_list", back_info_col)
            self.set_colors("hover.scrollable.selection_list", hover_col)
            self.set_colors("slider.scrollable.selection_list", slider_col)
            ### selection list frame ThumbButton
            self.set_colors("background.thumbbtn.selection_list", back_info_col)
            self.set_colors("backgroundbis.thumbbtn.selection_list", "sienna2")
            self.set_colors("hover.thumbbtn.selection_list", hover_col)

        elif theme == "ocra-minimal":
            header_col = "LightGoldenrod4"
            back_info_col = "LightGoldenrod3"
            btn_col = "LightGoldenrod2"
            hover_col = "LightGoldenrod1"
            slider_col = "khaki2"
            current_col = "goldenrod3"
            deselected_col = "red3"

            self.set_colors("background.frame_crop", back_info_col)
            self.set_colors("background.frame", back_info_col)
            self.set_colors("background.label", back_info_col)
            self.set_colors("background.header", header_col)

            self.set_colors("background.button", btn_col)
            self.set_colors("hover.button", hover_col)

            self.set_colors("background.chkbtn", back_info_col)
            self.set_colors("hover.chkbtn", hover_col)
            self.set_colors("select.chkbtn", btn_col)

            self.set_colors("background.scrollable", back_info_col)
            self.set_colors("hover.scrollable", hover_col)
            self.set_colors("slider.scrollable", slider_col)

            self.set_colors("background.thumbbtn", back_info_col)
            self.set_colors("backgroundbis.thumbbtn.photo_list", current_col)
            self.set_colors("backgroundbis.thumbbtn.selection_list", deselected_col)
            self.set_colors("hover.thumbbtn", hover_col)

        self._state_colors(logg)

    def set_colors(self, req_element, color):
        """Set the color of the specified element, defined as group.etype.element

        If the dict for that element/level does not exist, create it on the fly

        group.etype is automatically seen as group.etype.standard
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.set_colors")
        #  logg.setLevel("TRACE")
        logg.trace(f"Setting color {color} for {req_element}")
        elem_tree = req_element.split(".")
        logg.trace(f"Split in {elem_tree}")

        group = elem_tree[0]
        if not group in self.colors:
            self.colors[group] = {}

        etype = elem_tree[1]
        if not etype in self.colors[group]:
            self.colors[group][etype] = {}

        if len(elem_tree) > 2:
            element = elem_tree[2]
        else:
            element = "standard"

        self.colors[group][etype][element] = color

    def get_colors(self, req_element):
        """Return the color of the requested element, in the current theme
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.get_colors")
        logg.setLevel("TRACE")
        logg.trace(f"Getting color for {req_element}")
        #  group, element = req_element.split(".")
        #  logg.trace(f"Color for {group}:{element} is {self.colors[group][element]}")

        elem_tree = req_element.split(".")
        logg.trace(f"Split in {elem_tree}")

        group = elem_tree[0]
        etype = elem_tree[1]
        if len(elem_tree) > 2 and elem_tree[2] in self.colors[group][etype]:
            element = elem_tree[2]
        else:
            element = "standard"

        logg.trace(f"Color for {group}:{etype}:{element}")
        #  is {self.colors[group][etype][element]}"

        return self.colors[group][etype][element]

    def _state_colors(self, logg):
        for g in self.colors:
            logg.trace(f"Group {g}")

            for t in self.colors[g]:
                logg.trace(f"    Element type {t}")

                for e in self.colors[g][t]:
                    logg.trace(f"        Element {e:<20} color {self.colors[g][t][e]}")
