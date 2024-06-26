import argparse
import logging
import os
import re
import sys
from nis import cat
from pathlib import Path
from typing import Union

from yt_dlp import YoutubeDL

from extractor import model, pipeline


def _episode_short_name(name: str) -> str:
    match = re.findall(r"Campaign\s+(\d+),\s+Episode\s+(\d+)", name)
    if not match:
        raise Exception(f"Could not parse episode name: {name}")
    campaign, episode = match[0]
    return f"C{campaign}E{int(episode):0>3}"


def _relative_symlink(target: Union[Path, str], destination: Union[Path, str]):
    """Create a symlink pointing to ``target`` from ``location``.
    Args:
        target: The target of the symlink (the file/directory that is pointed to)
        destination: The location of the symlink itself.

    https://gist.github.com/willprice/311faace6fb4f514376fa405d2220615
    """
    target = Path(target)
    destination = Path(destination)
    target_dir = destination.parent
    target_dir.mkdir(exist_ok=True, parents=True)
    relative_source = os.path.relpath(target, target_dir)
    dir_fd = os.open(str(target_dir.absolute()), os.O_RDONLY)
    try:
        os.symlink(relative_source, destination.name, dir_fd=dir_fd)
    finally:
        os.close(dir_fd)


logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
    prog="critrole_playlist",
    description="Updates color information for a Critical Role playlist"
)
parser.add_argument("playlist",
                    type=str,
                    help="URL to the playlist.")
parser.add_argument("frames",
                    type=str,
                    help="Path to the frames directory. 'frame_(mask)_(fullhd|hd|sd).png' define valid frames and '(hue|temp)_<name>_(fullhd|hd|sd).png' define hue/temperature areas (in alphabetic order).")
parser.add_argument("output",
                    type=str,
                    help="Path to the color output directory.")
parser.add_argument("-w", "--workers",
                    default=1,
                    type=int,
                    help="Number of workers to use (default=1).")

arguments = parser.parse_args()

with YoutubeDL({"quiet": True, "no_warnings": True, "noprogress": True, "extract_flat": True}) as yt:
    info = yt.extract_info(arguments.playlist, download=False)
    if info is None:
        raise Exception("Could not extract playlist information")
entries: list = info['entries']
url_id_name: list[tuple[str, str, str]] = list(
    map(lambda x: (x['url'], x['id'], x['title']), entries))

existing_episodes: list[str] = list(filter(lambda f: f.endswith(
    ".json"), os.listdir(arguments.output)))
new_url_id_name: list[tuple[str, str, str]] = []
for url, id, name in url_id_name:
    try:
        if f"{_episode_short_name(name)}_{id}.json" in existing_episodes:
            logging.info(f'Skipping "{name}" ({id})')
            continue
    except Exception as e:
        logging.error(f'Error processing "{name}" ({id}): {e}')
        continue

    new_url_id_name.append((url, id, name))

empty: list[str] = []
for url, id, name in new_url_id_name:
    logging.info(f'Extracting "{name}" ({id})')
    updates = pipeline.extract_from_youtube_video(
        arguments.frames, url, workers=arguments.workers)
    if len(updates) == 0:
        empty.append(f'No colors extracted for "{name}" ({id})')
        continue

    with open(os.path.join(arguments.output, f"{_episode_short_name(name)}_{id}.json"), "w") as f:
        f.write(model.to_json(updates, url))

    # Create a symlink so the data can be accessed by ID as well.
    _relative_symlink(
        os.path.join(arguments.output,
                     f"{_episode_short_name(name)}_{id}.json"),
        os.path.join(arguments.output,
                     f"{id}.json"),
    )

if len(empty) > 0:
    for error in empty:
        logging.error(error)
    sys.exit(-1)
