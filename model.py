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

    def toggleInputFolder(self, state):
        log = logging.getLogger(f"c.{__name__}.toggleInputFolder")
        log.info(f"Setting new input_folder state")

        state = {x: state[x].get() for x in state}
        log.log(5, f"state {state}")

        if sum((state[x] for x in state)) > 0:
            # at least one still toggled
            self.input_folders.set(state)
        else:
            # no folders toggled, revert to previous state
            log.warn("At least one input folder has to be selected")
            self.input_folders._docallbacks()


class ModelCrop:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")
