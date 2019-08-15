import logging

from observable import Observable


class Model:
    def __init__(self, input_folder):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        #  self.model_crop = ModelCrop(


class ModelCrop:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")
