# from utils import AUDITED_FULL_SCRIPT_PATH, TOTAL_EPISODES, get_output_episode_path
from utils.constants import (
    AUDITED_FULL_SCRIPT_PATH,
    TOTAL_EPISODES,
    get_output_episode_path,
)
import utils.utils as utils

import cn2an
import os

script_lines: list[str] = []
with open(AUDITED_FULL_SCRIPT_PATH, "r", encoding="utf-8") as f:
    script_lines = f.readlines()



########################################################
# EXTRACT EPISODE SCRIPTS
########################################################


# EXTRACT EPISODE LINE START INDICES
episode_line_start_indices: dict[int, int] = {}

for line_idx, line in enumerate(script_lines):
    # the script content starts from line 180
    if line_idx < 179:
        continue
    # detect potential episode lines
    if not line.startswith("第"):
        continue

    # extract episode number
    episode_number_cn = line.split("第")[1].split("回")[0]
    episode_number = int(cn2an.cn2an(episode_number_cn))

    episode_line_start_indices[episode_number] = line_idx


# EXTRACT EPISODE TEXT
episode_scripts: dict[int, str] = {}

for episode_number in range(1, TOTAL_EPISODES + 1):
    episode_line_start_idx = episode_line_start_indices[episode_number]
    episode_line_end_idx = episode_line_start_indices[episode_number + 1]

    episode_script = "".join(script_lines[episode_line_start_idx:episode_line_end_idx])
    episode_script = utils.remove_page_numbers(episode_script)
    episode_script = episode_script.strip()

    episode_scripts[episode_number] = episode_script


# SAVE EPISODE SCRIPTS
for episode_number in range(1, TOTAL_EPISODES + 1):
    episode_script = episode_scripts[episode_number]

    output_folder_path = get_output_episode_path(episode_number)
    os.makedirs(output_folder_path, exist_ok=True)

    with open(
        os.path.join(output_folder_path, "script.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(episode_script)

        

########################################################
# EXTRACT SCENE SCRIPTS
########################################################

from typing import TypedDict, List

class Scene(TypedDict):
    line_idx: int
    scene_number: int
    scene_script: str
    scene_description: str

def extract_scene(script_lines: List[str]) -> List[ Scene]:

    # find scene headings
    scene_headings = []

    for i, line in enumerate(script_lines):
        line = line.strip()
        if line.startswith("【") and line.endswith("】"):
            scene_heading = {
                "line_idx": i,
                "scene_description": line,
                "scene_number": 0  # Temporary value
            }
            scene_headings.append(scene_heading)
    # sort by line_idx
    scene_headings.sort(key=lambda x: x["line_idx"])

    # extract scene scripts
    scene_scripts: List[Scene] = []
    episode_line_count = len(script_lines)
    scene_count_in_episode = len(scene_headings)

    for scene_idx, scene_heading in enumerate(scene_headings):
        scene_number = scene_idx + 1
        scene_line_start_idx = scene_heading["line_idx"]

        if scene_idx == scene_count_in_episode - 1:
            scene_line_end_idx = episode_line_count
        else:
            scene_line_end_idx = scene_headings[scene_idx + 1]["line_idx"]

        scene_script = "\n".join(script_lines[scene_line_start_idx:scene_line_end_idx])

        scene_scripts.append({
            "scene_number": scene_number,
            "scene_script": scene_script,
            "scene_description": scene_heading["scene_description"],
        })
    return scene_scripts

for episode_number in range(1, TOTAL_EPISODES + 1):
    episode_script = episode_scripts[episode_number]
    episode_script_lines = episode_script.split("\n")

    scene_scripts = extract_scene(episode_script_lines)

    for scene_script in scene_scripts:
        scene_number = scene_script["scene_number"]
        scene_script_text = scene_script["scene_script"]

        output_folder_path = get_output_episode_path(episode_number)
        os.makedirs(output_folder_path, exist_ok=True)

        scene_folder_path = os.path.join(output_folder_path, f"scenes")
        os.makedirs(scene_folder_path, exist_ok=True)

        with open(
            os.path.join(scene_folder_path, f"scene_{scene_number}.txt"), "w", encoding="utf-8"
        ) as f:
            f.write(scene_script_text)
