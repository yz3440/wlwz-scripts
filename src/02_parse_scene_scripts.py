from utils.constants import EPISODES_OUTPUT_PATH, TOTAL_EPISODES
import os
import json

from utils.parser import (
    llm_parse_scene,
    extract_json,
    find_missing_parts,
    validate_scene_script_json,
)
from utils.utils import Scene, find_all_scenes

all_scenes: list[Scene] = find_all_scenes()

for scene in all_scenes:
    print(f"Episode {scene.episode_number} scene {scene.scene_number}")
    print(f"Scene file path: {scene.scene_file_path}")
    if scene.parsed:
        print(f"Already parsed, skipping...")
        continue

    scene_text = open(scene.scene_file_path).read()

    parsed_scene_text = llm_parse_scene(scene_text, os.getenv("ANTHROPIC_API_KEY"))
    # parsed_scene_text = open(scene.parsed_scene_json_path).read()
    try:
        parsed_scene_dict = extract_json(parsed_scene_text)
        validate_scene_script_json(parsed_scene_dict)
    except Exception as e:
        print(
            f"Response not valid JSON / not valid schema, writing to {scene.parsing_error_result_path}"
        )
        print(e)
        with open(scene.parsing_error_result_path, "w") as f:
            f.write(parsed_scene_text)
        # input("Press Enter to continue...")
        continue

    with open(scene.parsed_scene_json_path, "w") as f:
        json.dump(parsed_scene_dict, f, indent=2, ensure_ascii=False)

    missing_parts = find_missing_parts(parsed_scene_text, scene_text)
    if len(missing_parts) > 0:
        print(f"Missing parts: {missing_parts}")
        with open(scene.missing_text_parts_path, "w") as f:
            f.write("\n".join(missing_parts))
        # input("Press Enter to continue...")
    else:
        print("No missing parts")
