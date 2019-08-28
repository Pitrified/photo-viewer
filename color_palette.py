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
            self.colors["background"]["frame_crop_prim"] = "SeaGreen1"
            self.colors["background"]["frame_crop_echo"] = "SeaGreen2"

            ##################
            # metadata frame #
            ##################
            self.colors["background"]["frame_metadata"] = "SeaGreen3"

            ###################
            # path info frame #
            ###################
            self.colors["background"]["frame_path_info"] = "SeaGreen4"

            ## output frame
            self.colors["background"]["output_frame"] = "SeaGreen4"
            ### output header
            self.colors["background"]["output_frame_header"] = "SeaGreen3"
            ### output button set folder
            self.colors["background"]["output_setfolder"] = "SeaGreen3"
            self.colors["hover"]["output_setfolder"] = "SeaGreen2"
            ### output label
            self.colors["background"]["output_label"] = "SeaGreen4"

            ## input frame
            self.colors["background"]["input_frame"] = "SeaGreen4"
            ### input header
            self.colors["background"]["input_frame_header"] = "SeaGreen3"
            ### input button add folder
            self.colors["background"]["input_addfolder"] = "SeaGreen3"
            self.colors["hover"]["input_addfolder"] = "SeaGreen2"
            ### input checkbuttons folder
            self.colors["background"]["input_chkbtn"] = "SeaGreen4"
            self.colors["hover"]["input_chkbtn"] = "SeaGreen2"
            # ... this controls the background of the check in the Checkbutton
            self.colors["select"]["input_chkbtn"] = "SeaGreen3"

            ## photo list frame
            self.colors["background"]["photo_list_frame"] = "SeaGreen4"
            ### photo list frame header
            self.colors["background"]["photo_list_frame_header"] = "SeaGreen4"
            ### photo list frame ScrollableFrame
            self.colors["background"]["photo_list_scrollable"] = "SeaGreen4"
            self.colors["hover"]["photo_list_scrollable"] = "SkyBlue2"
            self.colors["slider"]["photo_list_scrollable"] = "DeepSkyBlue4"
            ### photo list frame ThumbButton
            self.colors["background"]["photo_list_thumbbtn"] = "SeaGreen4"
            self.colors["backgroundbis"]["photo_list_thumbbtn"] = "DeepSkyBlue2"
            self.colors["hover"]["photo_list_thumbbtn"] = "SkyBlue2"

            ## selection list frame
            self.colors["background"]["selection_list_frame"] = "SeaGreen4"
            ### selection list frame header
            self.colors["background"]["selection_list_frame_header"] = "SeaGreen4"
            ### selection list frame ScrollableFrame
            self.colors["background"]["selection_list_scrollable"] = "SeaGreen4"
            self.colors["hover"]["selection_list_scrollable"] = "SkyBlue2"
            self.colors["slider"]["selection_list_scrollable"] = "DeepSkyBlue3"
            ### selection list frame ThumbButton
            self.colors["background"]["selection_list_thumbbtn"] = "SeaGreen4"
            self.colors["backgroundbis"]["selection_list_thumbbtn"] = "sienna2"
            self.colors["hover"]["selection_list_thumbbtn"] = "SkyBlue2"

        elif theme == "blue1":
            ###############
            # crop frames #
            ###############
            self.colors["background"]["frame_crop_prim"] = "SteelBlue1"
            self.colors["background"]["frame_crop_echo"] = "SteelBlue2"

            ##################
            # metadata frame #
            ##################
            self.colors["background"]["frame_metadata"] = "SteelBlue3"

            ###################
            # path info frame #
            ###################
            header_col = "SkyBlue4"
            back_info_col = "SkyBlue3"
            btn_col = "SkyBlue2"
            hover_col = "LightSkyBlue2"
            slider_col = "SteelBlue3"

            self.colors["background"]["frame_path_info"] = back_info_col

            ## output frame
            self.colors["background"]["output_frame"] = back_info_col
            ### output header
            self.colors["background"]["output_frame_header"] = header_col
            ### output button set folder
            self.colors["background"]["output_setfolder"] = btn_col
            self.colors["hover"]["output_setfolder"] = hover_col
            ### output label
            self.colors["background"]["output_label"] = back_info_col

            ## input frame
            self.colors["background"]["input_frame"] = back_info_col
            ### input header
            self.colors["background"]["input_frame_header"] = header_col
            ### input button add folder
            self.colors["background"]["input_addfolder"] = btn_col
            self.colors["hover"]["input_addfolder"] = hover_col
            ### input checkbuttons folder
            self.colors["background"]["input_chkbtn"] = back_info_col
            self.colors["hover"]["input_chkbtn"] = hover_col
            # ... this controls the background of the check in the Checkbutton
            self.colors["select"]["input_chkbtn"] = btn_col

            ## photo list frame
            self.colors["background"]["photo_list_frame"] = back_info_col
            ### photo list frame header
            self.colors["background"]["photo_list_frame_header"] = header_col
            ### photo list frame ScrollableFrame
            self.colors["background"]["photo_list_scrollable"] = back_info_col
            self.colors["hover"]["photo_list_scrollable"] = hover_col
            self.colors["slider"]["photo_list_scrollable"] = slider_col
            ### photo list frame ThumbButton
            self.colors["background"]["photo_list_thumbbtn"] = back_info_col
            self.colors["backgroundbis"]["photo_list_thumbbtn"] = "DeepSkyBlue2"
            self.colors["hover"]["photo_list_thumbbtn"] = hover_col

            ## selection list frame
            self.colors["background"]["selection_list_frame"] = back_info_col
            ### selection list frame header
            self.colors["background"]["selection_list_frame_header"] = header_col
            ### selection list frame ScrollableFrame
            self.colors["background"]["selection_list_scrollable"] = back_info_col
            self.colors["hover"]["selection_list_scrollable"] = hover_col
            self.colors["slider"]["selection_list_scrollable"] = slider_col
            ### selection list frame ThumbButton
            self.colors["background"]["selection_list_thumbbtn"] = back_info_col
            self.colors["backgroundbis"]["selection_list_thumbbtn"] = "sienna2"
            self.colors["hover"]["selection_list_thumbbtn"] = hover_col

    def get_colors(self, req_element):
        """Return the color of the requested element, in the current theme
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.get_colors")
        #  logg.setLevel("TRACE")
        logg.trace(f"Getting color for {req_element}")
        group, element = req_element.split(".")
        logg.trace(f"Color for {group}:{element} is {self.colors[group][element]}")
        return self.colors[group][element]
