import os.path
import sys

import sam_interface
import logging

logging.basicConfig(
    format='(%(asctime)s) [%(levelname)-8.8s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        menu = sam_interface.ui.MainMenuInterface()
        menu.start()

    else:
        filename = sys.argv[1]
        if not os.path.isfile(filename):
            logging.fatal("Specified file '{}' does not exist!".format(filename))
            sys.exit(-1)

        if filename.endswith(".dat"):
            logging.info("Loading segment manager backup from file '{}'...".format(os.path.abspath(filename)))
            sm = sam_interface.SegmentManager.load(filename)

        else:
            logging.info("Loading segment manager on image '{}'...".format(os.path.abspath(filename)))
            sm = sam_interface.SegmentManager(sys.argv[1])

        logging.info("Loading complete. Starting interface...")
        interface = sam_interface.ui.SAMInterface(sm)
        interface.start()
