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
        print("Usage:")
        print("  {} [filename]".format(sys.argv[0]))
        sys.exit(-1)

    filename = sys.argv[1]
    if not os.path.isfile(filename):
        logging.fatal("Specified file '{}' does not exist!".format(filename))
        sys.exit(-1)

    if filename.endswith(".dat"):
        logging.info("Loading segment manager backup from file '{}'...".format(os.path.abspath(filename)))
        sm = sam_interface.SegmentManager.load(filename)

    else:
        sm = sam_interface.SegmentManager(sys.argv[1])
        sm.save("segment_manager.dat")

    logging.info("Loading complete. Starting interface...")
    i = sam_interface.ui.SAMInterface(sm)
    i.start()
