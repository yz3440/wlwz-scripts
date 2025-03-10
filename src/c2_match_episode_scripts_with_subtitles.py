#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from typing import List, Dict, Tuple, Any, Optional
import heapq
import pysrt
from difflib import SequenceMatcher

from utils.constants import TOTAL_EPISODES, CONTENT_OUTPUT_PATH, get_output_episode_path
from utils.utils import Scene, find_all_scenes
from utils.parser import llm_parse_scene, extract_json, find_missing_parts

# Episodes to process - change this to process different episodes
EPISODES_TO_PROCESS = [1]


def is_scene_parsed_successfully(scene: Scene) -> bool:
    """
    Check if a scene has been parsed successfully
    """
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


def consolidate_scene_scripts(episode_number: int) -> Optional[Dict]:
    """
    Consolidate individual scene scripts into a single episode script
    Returns the consolidated script dictionary or None if consolidation failed
    """
    print(f"Consolidating scene scripts for Episode {episode_number}")

    # Find all scenes
    all_scenes = find_all_scenes()

    # Group scenes by episode number
    episode_scenes = {}
    for scene in all_scenes:
        if scene.episode_number not in episode_scenes:
            episode_scenes[scene.episode_number] = []
        episode_scenes[scene.episode_number].append(scene)

    # Sort scenes by scene number
    if episode_number in episode_scenes:
        episode_scenes[episode_number].sort(key=lambda x: x.scene_number)
    else:
        print(f"No scenes found for Episode {episode_number}")
        return None

    # Check if all scenes were parsed successfully
    is_all_scenes_parsed_successfully = True
    for scene in episode_scenes[episode_number]:
        if not is_scene_parsed_successfully(scene):
            is_all_scenes_parsed_successfully = False
            break

    if not is_all_scenes_parsed_successfully:
        print("Not all scenes parsed successfully, skipping...")
        return None

    episode_output_path = get_output_episode_path(episode_number)

    # Consolidate parsed scenes into a list of dictionaries
    scenes_dicts = []
    for scene in episode_scenes[episode_number]:
        with open(scene.parsed_scene_json_path, "r", encoding="utf-8") as f:
            scene_dict = json.load(f)
        scene_dict = {"sceneNumber": scene.scene_number, **scene_dict}
        scenes_dicts.append(scene_dict)

    # Get episode name from original script
    episode_original_script_path = os.path.join(episode_output_path, "script.txt")
    with open(episode_original_script_path, "r", encoding="utf-8") as f:
        episode_name = f.read().split("\n")[0]

    consolidated_script = {
        "name": episode_name,
        "episodeNumber": episode_number,
        "scenes": scenes_dicts,
    }

    consolidated_script_path = os.path.join(episode_output_path, "script.json")
    with open(consolidated_script_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_script, f, indent=2, ensure_ascii=False)

    print(f"Consolidated script saved to {consolidated_script_path}")
    return consolidated_script


def clean_text(text: str) -> str:
    """
    Clean text by removing escape characters and splitting on punctuation
    """
    # Remove escape characters
    text = text.replace('\\"', "")

    # Split by punctuation and rejoin with spaces
    parts = re.split(r"[（）—().,!?;:，。！？；：、…~【】…''" "]", text)
    # remove empty parts
    parts = [part for part in parts if part]
    # strip parts
    parts = [part.strip() for part in parts]

    return " ".join(parts).strip()


def generate_line_ids(script_data: Dict) -> Dict:
    """
    Generate line IDs for each line in the script JSON
    Format: ep{episode}-s{scene}-l{line}
    """
    episode_number = script_data["episodeNumber"]
    scenes = script_data["scenes"]

    # Deep copy the script data to avoid modifying the original
    script_with_ids = {
        "name": script_data["name"],
        "episodeNumber": episode_number,
        "scenes": [],
    }

    for scene_idx, scene in enumerate(scenes, 1):
        scene_with_ids = scene.copy()
        performances = scene.get("performances", [])
        new_performances = []

        line_idx = 1
        for perf in performances:
            new_perf = perf.copy()

            if perf["type"] == "dialog":
                new_performances_in_dialog = []
                for dialog_perf in perf.get("performances", []):
                    new_dialog_perf = dialog_perf.copy()

                    if dialog_perf["type"] == "line":
                        line_id = f"ep{episode_number}-s{scene_idx}-l{line_idx}"
                        line_text = dialog_perf["line"]
                        new_dialog_perf["lineId"] = line_id
                        new_dialog_perf["textToMatch"] = clean_text(line_text)
                        line_idx += 1

                    new_performances_in_dialog.append(new_dialog_perf)

                new_perf["performances"] = new_performances_in_dialog

            new_performances.append(new_perf)

        scene_with_ids["performances"] = new_performances
        script_with_ids["scenes"].append(scene_with_ids)

    return script_with_ids


def extract_lines_from_script(script_data: Dict) -> List[Dict]:
    """
    Extract all lines from the script with their IDs and text to match
    """
    lines = []
    for scene in script_data["scenes"]:
        for perf in scene.get("performances", []):
            if perf["type"] == "dialog":
                for dialog_perf in perf.get("performances", []):
                    if dialog_perf["type"] == "line" and "lineId" in dialog_perf:
                        lines.append(
                            {
                                "lineId": dialog_perf["lineId"],
                                "line": dialog_perf["line"],
                                "textToMatch": dialog_perf["textToMatch"],
                                "speaker": perf.get("speaker", ""),
                            }
                        )
    return lines


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using SequenceMatcher
    """
    # For Chinese text, we can use character-by-character similarity
    return SequenceMatcher(None, text1, text2).ratio()


def ordered_character_match(srt_text: str, script_text: str) -> float:
    """
    Calculate ordered character match score that tolerates missing or altered characters
    but preserves the original order of characters.

    Returns a score between 0 and 1, with 1 being a perfect match.
    """
    if not srt_text or not script_text:
        return 0.0

    # Use dynamic programming to find the longest common subsequence
    srt_len = len(srt_text)
    script_len = len(script_text)

    # Create a matrix to store the length of LCS
    dp = [[0] * (script_len + 1) for _ in range(srt_len + 1)]

    # Fill the dp table
    for i in range(1, srt_len + 1):
        for j in range(1, script_len + 1):
            if srt_text[i - 1] == script_text[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Calculate the score as the ratio of LCS to the length of SRT text
    lcs_length = dp[srt_len][script_len]
    return lcs_length / srt_len


def find_best_match(
    srt_text: str, script_lines: List[Dict], start_index: int = 0
) -> Tuple[int, float]:
    """
    Find the best match for an SRT line from the script lines
    Returns the index of the best match and the similarity score
    """
    best_match_idx = -1
    best_score = 0

    # Skip empty SRT lines
    if not srt_text.strip():
        return -1, 0

    for i in range(start_index, len(script_lines)):
        script_line = script_lines[i]
        text_to_match = script_line["textToMatch"]

        # Calculate ordered character match score
        ocm_score = ordered_character_match(srt_text, text_to_match)

        # Calculate standard similarity score
        std_score = calculate_similarity(srt_text, text_to_match)

        # Combine scores with more weight to ordered character match
        combined_score = (ocm_score * 0.7) + (std_score * 0.3)

        if combined_score > best_score:
            best_score = combined_score
            best_match_idx = i

    return best_match_idx, best_score


def match_range(
    srt_lines: List[Dict],
    script_lines: List[Dict],
    start_srt_idx: int,
    end_srt_idx: int,
    start_script_idx: int,
    end_script_idx: int,
) -> Dict[int, int]:
    """
    Match a range of SRT lines with a range of script lines
    Returns a dictionary mapping SRT indices to script indices
    """
    matches = {}

    # For each SRT line in the range, find the best match within the script range
    for srt_idx in range(start_srt_idx, end_srt_idx):
        best_match_idx = -1
        best_score = 0

        for script_idx in range(start_script_idx, end_script_idx):
            ocm_score = ordered_character_match(
                srt_lines[srt_idx]["text"], script_lines[script_idx]["textToMatch"]
            )

            std_score = calculate_similarity(
                srt_lines[srt_idx]["text"], script_lines[script_idx]["textToMatch"]
            )

            combined_score = (ocm_score * 0.7) + (std_score * 0.3)

            if combined_score > best_score:
                best_score = combined_score
                best_match_idx = script_idx

        # Only add the match if the score is above a threshold
        if best_score > 0.3:
            matches[srt_idx] = best_match_idx

    return matches


def match_srt_with_script_recursive(
    srt_lines: List[Dict],
    script_lines: List[Dict],
    start_srt_idx: int,
    end_srt_idx: int,
    start_script_idx: int,
    end_script_idx: Optional[int] = None,
) -> Dict[int, int]:
    """
    Recursively match SRT lines with script lines
    """
    if end_script_idx is None:
        end_script_idx = len(script_lines)

    # Base case: if there's only one SRT line or script line, try to match directly
    if start_srt_idx >= end_srt_idx or start_script_idx >= end_script_idx:
        return {}

    # If the range is small enough, use direct matching instead of recursive approach
    if end_srt_idx - start_srt_idx <= 5 or end_script_idx - start_script_idx <= 5:
        return match_range(
            srt_lines,
            script_lines,
            start_srt_idx,
            end_srt_idx,
            start_script_idx,
            end_script_idx,
        )

    # Find the longest SRT line in the current range
    longest_idx = start_srt_idx
    longest_length = len(srt_lines[start_srt_idx]["text"])

    for i in range(start_srt_idx + 1, end_srt_idx):
        length = len(srt_lines[i]["text"])
        if length > longest_length:
            longest_length = length
            longest_idx = i

    # Find the best match for the longest line
    match_idx, score = find_best_match(
        srt_lines[longest_idx]["text"], script_lines, start_script_idx
    )

    # If no good match found, try another approach
    if match_idx == -1 or score <= 0.3:
        # Split the SRT range and try matching each half
        mid_srt = (start_srt_idx + end_srt_idx) // 2

        # Recursively match the first half
        matches1 = match_srt_with_script_recursive(
            srt_lines,
            script_lines,
            start_srt_idx,
            mid_srt,
            start_script_idx,
            end_script_idx,
        )

        # Find the highest script index matched in the first half
        max_script_idx = start_script_idx
        if matches1:
            max_script_idx = max(matches1.values())

        # Recursively match the second half
        matches2 = match_srt_with_script_recursive(
            srt_lines,
            script_lines,
            mid_srt,
            end_srt_idx,
            max_script_idx,
            end_script_idx,
        )

        # Combine the matches
        matches1.update(matches2)
        return matches1

    # We found a match for the longest line
    matches = {longest_idx: match_idx}

    # Recursively match the lines before the longest line
    if longest_idx > start_srt_idx:
        before_matches = match_srt_with_script_recursive(
            srt_lines,
            script_lines,
            start_srt_idx,
            longest_idx,
            start_script_idx,
            match_idx + 1,  # +1 to include the matched line
        )
        matches.update(before_matches)

    # Recursively match the lines after the longest line
    if longest_idx < end_srt_idx - 1:
        after_matches = match_srt_with_script_recursive(
            srt_lines,
            script_lines,
            longest_idx + 1,
            end_srt_idx,
            match_idx,
            end_script_idx,
        )
        matches.update(after_matches)

    return matches


def post_process_matches(
    matches: Dict[int, int], srt_lines: List[Dict], script_lines: List[Dict]
) -> Dict[int, int]:
    """
    Post-process the matches to fix any obvious errors
    by checking the surrounding matches
    """
    fixed_matches = matches.copy()

    # Sort SRT indices
    srt_indices = sorted(matches.keys())

    for i in range(1, len(srt_indices) - 1):
        prev_srt_idx = srt_indices[i - 1]
        curr_srt_idx = srt_indices[i]
        next_srt_idx = srt_indices[i + 1]

        prev_script_idx = matches[prev_srt_idx]
        curr_script_idx = matches[curr_srt_idx]
        next_script_idx = matches[next_srt_idx]

        # If current match is inconsistent with surrounding matches
        if prev_script_idx == next_script_idx and curr_script_idx != prev_script_idx:
            # Check if current SRT line better matches with the script line
            # that surrounding matches point to
            curr_srt_text = srt_lines[curr_srt_idx]["text"]

            prev_script_match_score = ordered_character_match(
                curr_srt_text, script_lines[prev_script_idx]["textToMatch"]
            )

            curr_script_match_score = ordered_character_match(
                curr_srt_text, script_lines[curr_script_idx]["textToMatch"]
            )

            # If the match with surrounding script line is reasonably good,
            # update the match
            if (
                prev_script_match_score > 0.5
                or prev_script_match_score > curr_script_match_score
            ):
                fixed_matches[curr_srt_idx] = prev_script_idx

        # Special case: if current and next script indices are the same but previous is different
        # and consecutive SRT lines, check if previous SRT line should match with current script line
        if curr_script_idx == next_script_idx and curr_script_idx != prev_script_idx:
            if curr_srt_idx == prev_srt_idx + 1 and next_srt_idx == curr_srt_idx + 1:
                prev_srt_text = srt_lines[prev_srt_idx]["text"]
                curr_script_text = script_lines[curr_script_idx]["textToMatch"]

                match_score = ordered_character_match(prev_srt_text, curr_script_text)

                if match_score > 0.5:
                    fixed_matches[prev_srt_idx] = curr_script_idx

    return fixed_matches


def validate_srt_matches(episode_number: int) -> None:
    """
    Validate the SRT matches and generate a log file
    - Find indices that don't have a match result
    - Check if matched IDs are in ascending order
    """
    print(f"Validating matches for Episode {episode_number}")

    # Get paths
    episode_path = get_output_episode_path(episode_number)
    srt_path = os.path.join(episode_path, "subtitles_with_id.srt")
    log_path = os.path.join(episode_path, "subtitles_with_id.log")

    # Load SRT file
    srt_data = pysrt.open(srt_path, encoding="utf-8")

    # Initialize variables
    missing_matches = []
    order_violations = []
    last_episode = 0
    last_scene = 0
    last_line = 0
    line_id_pattern = r"\[ep(\d+)-s(\d+)-l(\d+)\]"

    # Check each subtitle entry
    for i, sub in enumerate(srt_data):
        match = re.search(line_id_pattern, sub.text)

        if not match:
            missing_matches.append(i)
            continue

        # Extract episode, scene, and line numbers
        ep_num = int(match.group(1))
        scene_num = int(match.group(2))
        line_num = int(match.group(3))

        # Check if the order is correct
        if ep_num < last_episode:
            order_violations.append(
                (
                    i,
                    f"Episode number decreased: ep{ep_num}-s{scene_num}-l{line_num} after ep{last_episode}-s{last_scene}-l{last_line}",
                )
            )
        elif ep_num == last_episode:
            if scene_num < last_scene:
                order_violations.append(
                    (
                        i,
                        f"Scene number decreased: ep{ep_num}-s{scene_num}-l{line_num} after ep{last_episode}-s{last_scene}-l{last_line}",
                    )
                )
            elif scene_num == last_scene and line_num <= last_line:
                # Note: We allow equal line numbers since multiple SRT lines can match to the same script line
                if line_num < last_line:
                    order_violations.append(
                        (
                            i,
                            f"Line number decreased: ep{ep_num}-s{scene_num}-l{line_num} after ep{last_episode}-s{last_scene}-l{last_line}",
                        )
                    )

        # Update last values
        last_episode = ep_num
        last_scene = scene_num
        last_line = line_num

    # Write log file
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Validation Report for Episode {episode_number}\n")
        f.write("=" * 50 + "\n\n")

        # Report missing matches
        f.write(f"Missing Matches ({len(missing_matches)} entries):\n")
        f.write("-" * 50 + "\n")
        if missing_matches:
            for idx in missing_matches:
                sub_text = srt_data[idx].text
                f.write(f"Index {idx}: {sub_text}\n")
        else:
            f.write("No missing matches found!\n")
        f.write("\n")

        # Report order violations
        f.write(f"Order Violations ({len(order_violations)} entries):\n")
        f.write("-" * 50 + "\n")
        if order_violations:
            for idx, violation in order_violations:
                sub_text = srt_data[idx].text
                f.write(f"Index {idx}: {violation}\n")
                f.write(f"Text: {sub_text}\n\n")
        else:
            f.write("No order violations found!\n")

    print(f"Validation complete. Results saved to {log_path}")
    print(
        f"Missing matches: {len(missing_matches)}, Order violations: {len(order_violations)}"
    )


def process_episode(episode_number: int, consolidate_scenes: bool = True) -> None:
    """
    Process an episode:
    1. Optionally consolidate scene scripts
    2. Generate line IDs for the script
    3. Match subtitles with script lines
    """
    print(f"Processing Episode {episode_number}")

    # Get paths
    episode_path = get_output_episode_path(episode_number)
    script_path = os.path.join(episode_path, "script.json")
    srt_path = os.path.join(episode_path, "subtitles.srt")
    output_script_path = os.path.join(episode_path, "script_w_id.json")

    # Step 1: Consolidate scene scripts if requested
    if consolidate_scenes:
        script_data = consolidate_scene_scripts(episode_number)
        if script_data is None:
            print(
                f"Failed to consolidate scenes for Episode {episode_number}, skipping..."
            )
            return
    else:
        # Load existing script
        if not os.path.exists(script_path):
            print(f"Script file not found for Episode {episode_number}, skipping...")
            return

        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)

    # Step 2: Generate line IDs and save as script_w_id.json
    script_with_ids = generate_line_ids(script_data)

    with open(output_script_path, "w", encoding="utf-8") as f:
        json.dump(script_with_ids, f, indent=2, ensure_ascii=False)

    print(f"Saved script with IDs to {output_script_path}")

    # Step 3: Extract lines from script
    script_lines = extract_lines_from_script(script_with_ids)

    # Check if SRT file exists
    if not os.path.exists(srt_path):
        print(f"SRT file not found for Episode {episode_number}, skipping matching...")
        return

    # Load SRT
    srt_data = pysrt.open(srt_path, encoding="utf-8")
    srt_lines = [
        {"index": i, "text": clean_text(sub.text)} for i, sub in enumerate(srt_data)
    ]

    # Match SRT lines with script lines
    matches = match_srt_with_script_recursive(
        srt_lines, script_lines, 0, len(srt_lines), 0, len(script_lines)
    )

    # Post-process matches to fix obvious errors
    matches = post_process_matches(matches, srt_lines, script_lines)

    # Create mapping from SRT index to line ID
    line_id_map = {}
    for srt_idx, script_idx in matches.items():
        line_id_map[srt_idx] = script_lines[script_idx]["lineId"]

    # Add line IDs to SRT file
    new_srt_path = os.path.join(episode_path, "subtitles_with_id.srt")

    for i, sub in enumerate(srt_data):
        if i in line_id_map:
            sub.text = f"{sub.text} [{line_id_map[i]}]"

    srt_data.save(new_srt_path, encoding="utf-8")

    print(f"Saved SRT with line IDs to {new_srt_path}")
    print(f"Matched {len(matches)} out of {len(srt_lines)} SRT lines")

    # Validate the matches
    validate_srt_matches(episode_number)


def main() -> None:
    """
    Main function to process all specified episodes
    """
    # Check if we need to consolidate scene scripts
    consolidate_scenes = (
        input("Do you want to consolidate scene scripts first? (y/n): ").lower().strip()
        == "y"
    )

    # Allow user to specify episodes to process
    if (
        input("Do you want to specify which episodes to process? (y/n): ")
        .lower()
        .strip()
        == "y"
    ):
        try:
            episodes_input = input(
                "Enter episode numbers separated by commas (e.g., 1,2,3): "
            )
            episodes = [int(ep.strip()) for ep in episodes_input.split(",")]
            if episodes:
                global EPISODES_TO_PROCESS
                EPISODES_TO_PROCESS = episodes
        except ValueError:
            print("Invalid input. Using default episodes.")

    print(f"Processing episodes: {EPISODES_TO_PROCESS}")

    for episode_number in EPISODES_TO_PROCESS:
        process_episode(episode_number, consolidate_scenes)


if __name__ == "__main__":
    main()
