from utils.constants import TOTAL_EPISODES, CONTENT_OUTPUT_PATH, get_output_episode_path
import os
import json

from utils.parser import llm_parse_scene, extract_json, find_missing_parts
from utils.utils import Scene, find_all_scenes

all_scenes: list[Scene] = find_all_scenes()


# group by episode number
episode_scenes = {}
for scene in all_scenes:
    if scene.episode_number not in episode_scenes:
        episode_scenes[scene.episode_number] = []
    episode_scenes[scene.episode_number].append(scene)

# sort scenes by scene number within each episode
for episode_number in episode_scenes:
    episode_scenes[episode_number].sort(key=lambda x: x.scene_number)


def is_scene_parsed_successfully(scene: Scene) -> bool:
    # if json file does not exist, failed
    if not os.path.exists(scene.parsed_scene_json_path):
        return False

    # if missing text parts file exists, failed
    if os.path.exists(scene.missing_text_parts_path):
        return False

    # if parsing error result file exists, failed
    if os.path.exists(scene.parsing_error_result_path):
        return False

    return True


consolidated_episodes = []

for i in range(1, TOTAL_EPISODES + 1):
    print(f"Episode {i}")

    is_all_scenes_parsed_successfully = True
    for scene in episode_scenes[i]:
        if not is_scene_parsed_successfully(scene):
            is_all_scenes_parsed_successfully = False
            break

    if not is_all_scenes_parsed_successfully:
        print("Not all scenes parsed successfully, skipping...")
        continue

    episode_output_path = get_output_episode_path(i)

    # consolidate parsed scenes into a list of dictionaries
    scenes_dicts = []
    for scene in episode_scenes[i]:
        scene_dict = {}
        with open(scene.parsed_scene_json_path, "r") as f:
            scene_dict = json.load(f)
        scene_dict = {"sceneNumber": scene.scene_number, **scene_dict}
        scenes_dicts.append(scene_dict)

    # get episode name from original script
    episode_original_script_path = os.path.join(episode_output_path, "script.txt")
    episode_name = (
        open(episode_original_script_path, "r", encoding="utf-8").read().split("\n")[0]
    )

    consolidated_script = {
        "name": episode_name,
        "episodeNumber": i,
        "scenes": scenes_dicts,
    }

    consolidated_script_path = os.path.join(episode_output_path, "script.json")
    with open(consolidated_script_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_script, f, indent=2, ensure_ascii=False)

    consolidated_episodes.append(consolidated_script)

print(f"Consolidated {len(consolidated_episodes)} episodes")

if len(consolidated_episodes) == TOTAL_EPISODES:
    print("All episodes consolidated successfully")

    # write all episodes to a single file
    consolidated_script_path = os.path.join(CONTENT_OUTPUT_PATH, "script.json")
    with open(consolidated_script_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_episodes, f, indent=2, ensure_ascii=False)
