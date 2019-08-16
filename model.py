import logging

from observable import Observable


class Model:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.output_folder = Observable("Not set not known")
        self.input_folders = Observable({})

        #  self.model_crop = ModelCrop(

    def setOutputFolder(self, output_folder_full):
        log = logging.getLogger(f"c.{__name__}.setOutputFolder")
        log.info(f"Setting output_folder to '{output_folder_full}'")
        self.output_folder.set(output_folder_full)

    def addInputFolder(self, input_folder_full):
        log = logging.getLogger(f"c.{__name__}.addInputFolder")
        log.info(f"Adding new input_folder '{input_folder_full}'")
        old_folders = self.input_folders.get()
        old_folders[input_folder_full] = True
        self.input_folders.set(old_folders)


class ModelCrop:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")
