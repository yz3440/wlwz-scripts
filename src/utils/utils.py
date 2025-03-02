# remove page numbers from script text
def remove_page_numbers(script_text: str) -> str:
    # Read all lines
    lines = script_text.split("\n")

    # Filter out lines that are just small numbers
    filtered_lines = []
    for line in lines:
        line = line.strip()
        try:
            num = int(line)
        except ValueError:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)


from .constants import EPISODES_OUTPUT_PATH, TOTAL_EPISODES
import os

from dataclasses import dataclass
from typing import List


@dataclass
class Scene:
    episode_number: int
    scene_number: int
    scene_file_path: str
    parsed_scene_json_path: str
    parsed: bool
    parsing_error_result_path: str
    missing_text_parts_path: str


def find_all_scenes() -> List[Scene]:
    all_scenes: List[Scene] = []
    for episode_number in range(1, TOTAL_EPISODES + 1):
        episode_output_path = os.path.join(
            EPISODES_OUTPUT_PATH, f"{episode_number:02d}"
        )
        scene_folder_path = os.path.join(episode_output_path, "scenes")
        scene_files = os.listdir(scene_folder_path)

        import re

        scene_files = [
            file for file in scene_files if re.match(r"scene_(\d+)\.txt", file)
        ]
        scene_files.sort()

        for scene_file in scene_files:
            scene_number = int(re.search(r"scene_(\d+)\.txt", scene_file).group(1))

            parsed_scene_json_path = os.path.join(
                scene_folder_path, f"scene_{scene_number}.json"
            )

            scene_json_exists = os.path.exists(parsed_scene_json_path)

            parsing_error_result_path = os.path.join(
                scene_folder_path, f"scene_{scene_number}.error.json"
            )
            missing_text_parts_path = os.path.join(
                scene_folder_path, f"scene_{scene_number}_missing_text_parts.text"
            )

            all_scenes.append(
                Scene(
                    episode_number=episode_number,
                    scene_number=scene_number,
                    scene_file_path=os.path.join(scene_folder_path, scene_file),
                    parsed_scene_json_path=parsed_scene_json_path,
                    parsed=scene_json_exists,
                    parsing_error_result_path=parsing_error_result_path,
                    missing_text_parts_path=missing_text_parts_path,
                )
            )

    # sort by episode_number and scene_number
    all_scenes.sort(key=lambda x: (x.episode_number, x.scene_number))

    return all_scenes
