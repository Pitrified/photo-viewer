import argparse
import logging

from os.path import abspath
from os.path import dirname
from os.path import join
from timeit import default_timer as timer

from controller import Controller


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="img_fold1",
        help="Path to starting folder",
    )

    parser.add_argument(
        "-lld",
        "--log_level_debug",
        type=str,
        default="INFO",
        help="Level for the debugging logger",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    # setup a logger for debugging purposes
    logdebug = logging.getLogger("c")
    logdebug.propagate = False
    #  logLevel = "WARN"
    logdebug.setLevel(logLevel)

    debug_console_handler = logging.StreamHandler()

    log_format_debug = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    #  log_format_debug = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_debug = '%(levelname)s: %(message)s'
    #  log_format_debug = "%(message)s"

    formatter = logging.Formatter(log_format_debug)
    debug_console_handler.setFormatter(formatter)

    logdebug.addHandler(debug_console_handler)

    # setup a logger for UI
    logui = logging.getLogger("UI")
    logui.propagate = False
    logLevel = "INFO"
    logui.setLevel(logLevel)

    ui_console_handler = logging.StreamHandler()
    log_format_ui = "%(levelname)s: %(message)s"
    formatter = logging.Formatter(log_format_ui)
    ui_console_handler.setFormatter(formatter)
    logui.addHandler(ui_console_handler)

    addLoggingLevel("TRACE", 5)


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            # Yes, logger takes its '*args' as 'args'
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


def test_run(input_folder):
    c = Controller(input_folder)
    c.run()


def main():
    args = parse_arguments()

    path_input = args.path_input
    log_level_debug = args.log_level_debug

    setup_logger(log_level_debug)

    recap = f"Startup settings: python3 photo_main.py"
    recap += f" --path_input {path_input}"
    recap += f" --log_level_debug {log_level_debug}"

    logmain = logging.getLogger(f"UI")
    logmain.info(recap)

    dir_file = abspath(dirname(__file__))
    input_folder = join(dir_file, path_input)
    test_run(input_folder)


if __name__ == "__main__":
    main()
