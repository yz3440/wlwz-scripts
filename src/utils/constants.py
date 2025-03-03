################################################################################
# SCRIPT METADATA
################################################################################

import os

CONTENT_SOURCE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "content-source")
)

CONTENT_OUTPUT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "content-output")
)

EPISODES_OUTPUT_PATH = os.path.abspath(os.path.join(CONTENT_OUTPUT_PATH, "episodes"))

AUDITED_FULL_SCRIPT_PATH = os.path.join(
    CONTENT_SOURCE_PATH, "community-scripts-audited.txt"
)


TOTAL_EPISODES = 80


def get_output_episode_path(episode_number: int) -> str:
    return os.path.join(EPISODES_OUTPUT_PATH, f"{episode_number}")


################################################################################
# Video Metadata
################################################################################

from dataclasses import dataclass
import json
from typing import Dict


@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int


@dataclass
class VideoMeta:
    episode_number: str
    youtube_url: str
    local_path: str
    width: int
    height: int
    subtitle_boundingbox: BoundingBox
    viewport_boundingbox: BoundingBox


VIDEO_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "video")
VIDEO_META_PATH = os.path.join(VIDEO_PATH, "video_meta.json")


def load_video_meta() -> list[VideoMeta]:
    with open(VIDEO_META_PATH) as f:
        data = json.load(f)
        return [
            VideoMeta(
                episode_number=int(item["episode_number"]),
                youtube_url=item["youtube_url"],
                local_path=os.path.join(VIDEO_PATH, "..", item["local_path"]),
                width=item["width"],
                height=item["height"],
                subtitle_boundingbox=BoundingBox(**item["subtitle_boundingbox"]),
                viewport_boundingbox=BoundingBox(**item["viewport_boundingbox"]),
            )
            for item in data
        ]


VIDEO_META = load_video_meta()
