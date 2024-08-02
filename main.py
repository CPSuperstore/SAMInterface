import sam_interface
import logging

logging.basicConfig(
    format='(%(asctime)s) [%(levelname)-8.8s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

# sm = sam_interface.SegmentManager("images/circle_pattern.png")
# sm.save("tmp.dat")

sm = sam_interface.SegmentManager.load("tmp.dat")
i = sam_interface.ui.SAMInterface(sm)
i.start()
print("MENU")
