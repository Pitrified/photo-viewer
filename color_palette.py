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

        self.colors["background"]["frame_crop_prim"] = "SeaGreen1"

    def get_colors(self, req_element):
        """Return the color of the requested element, in the current theme
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.get_colors")
        logg.setLevel("TRACE")
        logg.info(f"Getting color for {req_element}")
        group, element = req_element.split('.')
        logg.trace(f'Color for {group}:{element} is {self.colors[group][element]}')
        return self.colors[group][element]
