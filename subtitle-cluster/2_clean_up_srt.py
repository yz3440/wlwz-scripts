import re
from dataclasses import dataclass
from typing import List, Optional

# Path for input and output files
input_srt_file_path = "edited_subtitles.srt"
output_srt_file_path = "cleaned_subtitles.srt"

# Tolerance window in milliseconds (for a 25fps video, each frame is 40ms)
# Adjust this value to control how close subtitles need to be to merge
TOLERANCE_MS = 1000 / 25 * 25  # 25 frames tolerance
MERGE_SUBTITLE = True


def timestamp_to_ms(timestamp: str) -> int:
    """Convert an SRT timestamp (HH:MM:SS,MS) to milliseconds."""
    hours, minutes, seconds_ms = timestamp.split(":")
    seconds, milliseconds = seconds_ms.split(",")

    ms = int(milliseconds)
    ms += int(seconds) * 1000
    ms += int(minutes) * 60 * 1000
    ms += int(hours) * 60 * 60 * 1000

    return ms


def ms_to_timestamp(ms: int) -> str:
    """Convert milliseconds to an SRT timestamp (HH:MM:SS,MS)."""
    hours = ms // (3600 * 1000)
    ms %= 3600 * 1000
    minutes = ms // (60 * 1000)
    ms %= 60 * 1000
    seconds = ms // 1000
    ms %= 1000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


@dataclass
class Subtitle:
    index: int
    start_time: str
    end_time: str
    text: str

    def is_empty(self) -> bool:
        """Check if the subtitle text is empty."""
        return not self.text.strip()

    def can_merge_with(self, other: "Subtitle") -> bool:
        """Check if this subtitle can be merged with another one."""
        # Check if the text is the same (ignoring whitespace)
        if self.text.strip() != other.text.strip():
            return False

        # Convert timestamps to milliseconds
        self_end_ms = timestamp_to_ms(self.end_time)
        other_start_ms = timestamp_to_ms(other.start_time)

        # Check if the timestamps are within the tolerance window
        time_diff = abs(other_start_ms - self_end_ms)
        return time_diff <= TOLERANCE_MS

    def merge_with(self, other: "Subtitle") -> "Subtitle":
        """Merge this subtitle with another one."""
        return Subtitle(
            index=self.index,
            start_time=self.start_time,
            end_time=other.end_time,
            text=self.text.strip(),
        )

    def to_srt_format(self) -> str:
        """Convert subtitle to SRT format."""
        return f"{self.index}\n{self.start_time} --> {self.end_time}\n{self.text}\n"


def parse_srt_file(file_path: str) -> List[Subtitle]:
    """Parse an SRT file and return a list of Subtitle objects."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split file by double newline (which separates subtitle entries)
    subtitle_blocks = content.strip().split("\n\n")
    subtitles = []

    for block in subtitle_blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue  # Skip invalid blocks

        index = int(lines[0])
        time_line = lines[1]
        text = "\n".join(lines[2:])

        # Extract start and end times
        time_match = re.match(
            r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_line
        )
        if time_match:
            start_time, end_time = time_match.groups()
            subtitles.append(Subtitle(index, start_time, end_time, text))

    return subtitles


def clean_subtitles(subtitles: List[Subtitle]) -> List[Subtitle]:
    """Clean the subtitles by removing empty lines and merging consecutive identical texts."""
    # First, remove empty subtitles
    non_empty_subtitles = [sub for sub in subtitles if not sub.is_empty()]

    if MERGE_SUBTITLE:
        # Then, merge consecutive identical texts
        merged_subtitles = []
        i = 0
        while i < len(non_empty_subtitles):
            current_sub = non_empty_subtitles[i]

            # Look ahead to see if next subtitle can be merged
            while i + 1 < len(non_empty_subtitles) and current_sub.can_merge_with(
                non_empty_subtitles[i + 1]
            ):
                current_sub = current_sub.merge_with(non_empty_subtitles[i + 1])
                i += 1

            merged_subtitles.append(current_sub)
            i += 1
    else:
        merged_subtitles = non_empty_subtitles

    # Reindex the subtitles
    for i, sub in enumerate(merged_subtitles, 1):
        sub.index = i

    return merged_subtitles


def write_srt_file(subtitles: List[Subtitle], file_path: str) -> None:
    """Write subtitles to an SRT file."""
    with open(file_path, "w", encoding="utf-8") as file:
        content = "\n".join(sub.to_srt_format() for sub in subtitles)
        file.write(content)


def main():
    print(f"Reading subtitles from {input_srt_file_path}...")
    subtitles = parse_srt_file(input_srt_file_path)
    print(f"Found {len(subtitles)} subtitle entries.")

    print("Cleaning subtitles...")
    cleaned_subtitles = clean_subtitles(subtitles)
    print(f"After cleaning: {len(cleaned_subtitles)} subtitle entries.")

    print(f"Writing cleaned subtitles to {output_srt_file_path}...")
    write_srt_file(cleaned_subtitles, output_srt_file_path)
    print("Done!")


if __name__ == "__main__":
    main()
