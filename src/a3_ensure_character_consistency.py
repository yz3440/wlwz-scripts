from utils.constants import EPISODES_OUTPUT_PATH, TOTAL_EPISODES
import os
import json

from utils.parser import (
    llm_parse_scene,
    extract_json,
    find_missing_parts,
    validate_scene_script_json,
    extract_character_names,
    extract_speaker_names,
    extract_reactor_names,
)
from utils.utils import Scene, find_all_scenes

all_scenes: list[Scene] = find_all_scenes()


all_character_names_map = {}
for scene in all_scenes:

    if not os.path.exists(scene.parsed_scene_json_path):
        continue

    # load scene json as plain text
    with open(scene.parsed_scene_json_path, "r") as f:
        scene_text = f.read()

    character_names = extract_speaker_names(scene_text)
    for character_name in character_names:
        if character_name not in all_character_names_map:
            all_character_names_map[character_name] = [
                (
                    scene.episode_number,
                    scene.scene_number,
                )
            ]
        else:
            all_character_names_map[character_name].append(
                (scene.episode_number, scene.scene_number)
            )


for character_name in all_character_names_map:
    print(character_name)
    print(all_character_names_map[character_name])
