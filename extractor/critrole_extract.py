import argparse
import logging

from extractor import color, io, model, search
from extractor.data import YouTubeVideo

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
                    default=300,
                    type=int,
                    help="Initial step size in seconds to extract color updates (default=300s).")
parser.add_argument("-r", "--accuracy",
                    default=20.0,
                    type=float,
                    help="Maximum accuracy of binary search to refine color updates in seconds (default=20s).")
parser.add_argument("-t", "--threshold",
                    default=0.98,
                    type=float,
                    help="Threshold of a valid frame. (default=0.98).")
parser.add_argument("-c", "--cuttoff",
                    default=0.25,
                    type=float,
                    help="Brightness cutoff for color extraction. (default=0.25).")

arguments = parser.parse_args()
if arguments.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

frame_mask, frame, hues, temps = io.find_frames(
    arguments.frames, arguments.quality)

d = YouTubeVideo(arguments.video, arguments.quality)
sch = search.Extractor(
    color.Color(
        brightness_cutoff=0.25,
    ),
    hues,
    temps,
    frame_mask,
    frame,
    valid_threshold=arguments.threshold
)

s = search.Search(sch, d, step=arguments.step,
                  workers=arguments.workers, refinement_accuracy=arguments.accuracy)
updates = s.search()

with open(arguments.output, "w") as f:
    f.write(model.to_json(updates, arguments.video))
