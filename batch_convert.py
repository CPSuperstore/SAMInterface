import datetime
import logging
import os.path
import sys

import sam_interface


logging.basicConfig(
    format='(%(asctime)s) [%(levelname)-8.8s] %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def process_image(path: str, output_dir: str):
    if not os.path.isfile(path):
        logging.fatal("Specified file '{}' does not exist!".format(path))
        return

    if path.endswith(".dat"):
        logging.info("Loading segment manager backup from file '{}'...".format(os.path.abspath(path)))
        segment_manager = sam_interface.SegmentManager.load(path)

    else:
        logging.info("Loading segment manager on image '{}'...".format(os.path.abspath(path)))
        sam_checkpoint = sam_interface.preferences.get_sam_checkpoint()

        segment_manager = sam_interface.segment_manager.SegmentManager(
            path,
            checkpoint_key=sam_checkpoint["model_type"],
            checkpoint_path=sam_checkpoint["checkpoint_path"],
            auto_detect_masks=True, load_interactive_segmentation=False
        )

    name = os.path.splitext(os.path.basename(path))[0]

    logging.info(
        "Exporting files based on preferences defined in '{}'".format(
            os.path.abspath(sam_interface.preferences.PREFERENCES_FILE)
        )
    )
    prefs = sam_interface.preferences.get_preferences()
    export_prefs = prefs["export_options"]

    sam_interface.export.full_export(
        segment_manager, output_dir, name,
        export_prefs["save_mask_tree"],
        export_prefs["save_vector_tree"],
        export_prefs["save_raster"],
        export_prefs["save_centroids"],
        export_prefs["save_detail_mask_tree"],
        export_prefs["save_detail_vector_tree"],
        export_prefs["save_detail_raster"],
        export_prefs["min_area"],
        export_prefs["tolerance"]
    )


if __name__ == '__main__':
    batch_list = sys.argv[2:]
    batch_size = len(batch_list)

    for i, image_path in enumerate(batch_list):
        logging.info("Processing file '{}' ({} of {})".format(
            os.path.abspath(image_path), i + 1, batch_size
        ))

        start = datetime.datetime.now()
        process_image(image_path, sys.argv[1])
        end = datetime.datetime.now()

        logging.info("Took {}".format(end - start))
