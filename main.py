import sys

import sam_interface
import logging

logging.basicConfig(
    format='(%(asctime)s) [%(levelname)-8.8s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

if len(sys.argv) == 1:
    print("Usage:")
    print("  {} [filename]".format(sys.argv[0]))
    sys.exit(-1)

# sm = sam_interface.SegmentManager(sys.argv[1])
# sm.save("tmp.dat")

sm = sam_interface.SegmentManager.load("tmp.dat")

i = sam_interface.ui.SAMInterface(sm)
i.start()

# menu = sam_interface.ui.MainMenuInterface()
# menu.start()
