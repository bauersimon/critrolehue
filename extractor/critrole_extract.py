import argparse
import logging

from extractor import constants, model, pipeline

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog="critrole_extract",
    description="Extracts color information from Critical Role"
)
parser.add_argument("video",
                    type=str,
                    help="URL to the video.")
parser.add_argument("frames",
                    type=str,
                    help="Path to the frames directory. 'frame_(mask)_(fullhd|hd|sd).png' define valid frames and '(hue|temp)_<name>_(fullhd|hd|sd).png' define hue/temperature areas (in alphabetic order).")
parser.add_argument("output",
                    type=str,
                    help="Path to the color output file.")
parser.add_argument("-v", "--verbose",
                    action="store_true",
                    help="Enable verbose logging.")
parser.add_argument("-q", "--quality",
                    default="hd",
                    choices=["fullhd", "hd", "sd"],
                    help="Video quality to use - assumes the respective frames are present in the frame directory (default=hd).")
parser.add_argument("-w", "--workers",
                    default=1,
                    type=int,
                    help="Number of workers to use (default=1).")
parser.add_argument("-s", "--step",
                    default=constants.DEFAULT_SEARCH_STEP,
                    type=int,
                    help="Initial step size in seconds to extract color updates (default=300s).")
parser.add_argument("-r", "--accuracy",
                    default=constants.DEFAULT_REFINEMENT_ACCURACY,
                    type=float,
                    help="Maximum accuracy of binary search to refine color updates in seconds (default=20s).")
parser.add_argument("-t", "--threshold",
                    default=constants.DEFAULT_VALID_THRESHOLD,
                    type=float,
                    help="Threshold of a valid frame. (default=0.98).")
parser.add_argument("-c", "--cuttoff",
                    default=constants.DEFAULT_BRIGHTNESS_CUTOFF,
                    type=float,
                    help="Brightness cutoff for color extraction. (default=0.25).")

arguments = parser.parse_args()
if arguments.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

updates = pipeline.extract_from_youtube_video(
    arguments.frames,
    arguments.video,
    arguments.quality,
    arguments.cuttoff,
    arguments.threshold,
    arguments.step,
    arguments.workers,
    arguments.accuracy,
)

with open(arguments.output, "w") as f:
    f.write(model.to_json(updates, arguments.video))
