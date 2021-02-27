import logging


class Observable:
    """A wrapper around data, to link callbacks to it"""

    def __init__(self, initialValue=None):
        log = logging.getLogger(f"c.{__class__.__name__}.init")
        log.info("Start init")

        self.data = initialValue
        self.callbacks = {}

    def addCallback(self, func):
        log = logging.getLogger(f"c.{__class__.__name__}.addCallback")
        log.info("Adding callback")

        self.callbacks[func] = 1

    def delCallback(self, func):
        del self.callback[func]

    def _docallbacks(self):
        for func in self.callbacks:
            func(self.data)

    def set(self, data):
        log = logging.getLogger(f"c.{__class__.__name__}.set")
        log.setLevel("INFO")
        log.debug("Setting data")

        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None
