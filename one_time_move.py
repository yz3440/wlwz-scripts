def get_input_scene_json_path(episode_number: int, scene_number: int) -> str:
    return f"/Users/yfz/Developer/GitHub/video-subtitles-extract/output/武林外传 S1E{episode_number}/scenes/scene_{scene_number}.json"


def get_output_scene_json_path(episode_number: int, scene_number: int) -> str:
    return f"/Users/yfz/Developer/GitHub/wlwz-scripts/content-output/episodes/{episode_number:02d}/scenes/scene_{scene_number}.json"


import os
import shutil

for episode_number in range(1, 81):
    for scene_number in range(1, 100):
        input_scene_json_path = get_input_scene_json_path(episode_number, scene_number)
        if os.path.exists(input_scene_json_path):
            output_scene_json_path = get_output_scene_json_path(
                episode_number, scene_number
            )

            # copy input scene json to output scene json
            shutil.copy(input_scene_json_path, output_scene_json_path)
