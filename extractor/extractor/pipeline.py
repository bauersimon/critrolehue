from extractor import color, constants, data, io, model, search


def extract_from_youtube_video(
    frames_directory: str,
    video_url: str,
    quality: str = constants.DEFAULT_QUALITY,
    brightness_cutoff: float = constants.DEFAULT_BRIGHTNESS_CUTOFF,
    valid_threshold: float = constants.DEFAULT_VALID_THRESHOLD,
    step: int = constants.DEFAULT_SEARCH_STEP,
    workers: int = 1,
    refinement_accuracy: float = constants.DEFAULT_REFINEMENT_ACCURACY,
) -> list[model.ColorUpdate]:
    frame_mask, frame, hues, temps = io.find_frames(
        frames_directory, quality)

    d = data.YouTubeVideo(video_url, quality)
    sch = search.Extractor(
        color.Color(
            brightness_cutoff=brightness_cutoff,
        ),
        hues,
        temps,
        frame_mask,
        frame,
        valid_threshold=valid_threshold
    )

    s = search.Search(sch, d, step=step,
                      workers=workers, refinement_accuracy=refinement_accuracy)
    return s.search()
