import argparse
import logging

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
        help="path to input image to use",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def test_run(input_folder):
    c = Controller(input_folder)
    c.run()


def main():
    setup_logger()

    args = parse_arguments()

    path_input = args.path_input

    recap = f"python3 photo_main.py"
    recap += f" --path_input {path_input}"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    test_run(path_input)


if __name__ == "__main__":
    main()
