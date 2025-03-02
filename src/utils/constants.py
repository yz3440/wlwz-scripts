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
    return os.path.join(EPISODES_OUTPUT_PATH, f"{episode_number:02d}")
