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

        # crop frames
        self.colors["background"]["frame_crop_prim"] = "SeaGreen1"
        self.colors["background"]["frame_crop_echo"] = "SeaGreen2"

        # metadata frame
        self.colors["background"]["frame_metadata"] = "SeaGreen3"

        # path info frame
        self.colors["background"]["frame_path_info"] = "SeaGreen4"

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

        ## input frame

        ## output frame

    def get_colors(self, req_element):
        """Return the color of the requested element, in the current theme
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.get_colors")
        #  logg.setLevel("TRACE")
        logg.trace(f"Getting color for {req_element}")
        group, element = req_element.split(".")
        logg.trace(f"Color for {group}:{element} is {self.colors[group][element]}")
        return self.colors[group][element]
