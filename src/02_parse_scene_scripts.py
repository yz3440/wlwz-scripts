from utils.constants import EPISODES_OUTPUT_PATH, TOTAL_EPISODES
import os
import json

from utils.parser import llm_parse_scene, extract_json, find_missing_parts

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


for scene in find_all_scenes():
    print(f"Episode {scene.episode_number} scene {scene.scene_number}")
    print(f"Scene file path: {scene.scene_file_path}")
    if scene.parsed:
        print(f"Already parsed, skipping...")
        continue

    scene_text = open(scene.scene_file_path).read()

    parsed_scene_text = llm_parse_scene(scene_text, os.getenv("ANTHROPIC_API_KEY"))
    try:
        parsed_scene_dict = extract_json(parsed_scene_text)

    except Exception as e:
        print(f"Response not valid JSON, writing to {scene.parsing_error_result_path}")
        with open(scene.parsing_error_result_path, "w") as f:
            f.write(parsed_scene_text)
        continue

    with open(scene.parsed_scene_json_path, "w") as f:
        json.dump(parsed_scene_dict, f, indent=2)

    missing_parts = find_missing_parts(parsed_scene_text, scene_text)
    if len(missing_parts) > 0:
        print(f"Missing parts: {missing_parts}")
        with open(scene.missing_text_parts_path, "w") as f:
            f.write("\n".join(missing_parts))
    else:
        print("No missing parts")
