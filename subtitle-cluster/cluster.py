import csv
import difflib
import zhconv


def read_tsv(file_path):
    """
    Reads a TSV file and returns a list of dictionaries.
    Each dictionary contains keys: 'frame', 'text', 'confidence', and 'time'.
    """
    # Increase CSV field size limit to handle large fields
    csv.field_size_limit(5000000)

    rows = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(
            f, delimiter="\t", fieldnames=["frame", "text", "confidence", "time"]
        )
        for row in reader:
            try:
                row["frame"] = int(row["frame"])
            except Exception:
                continue
            try:
                row["time"] = int(row["time"])
            except Exception:
                continue

            row["text"] = row["text"].strip()
            # filter out all the symbols
            import re

            row["text"] = re.sub(r"[^\w\s]", "", row["text"])

            # convert to simplified chinese
            row["text"] = zhconv.convert(row["text"], "zh-cn")

            rows.append(row)
    return rows


def clean_text(text):
    """
    Cleans the text by removing double and single quotes and extra spaces.
    """
    if text is None:
        return None
    return text.replace('"', "").replace("'", "").strip()


def is_similar(text1, text2, threshold=0.8):
    """
    Returns True if text1 and text2 are similar based on the SequenceMatcher ratio.
    Uses cleaned text to ignore extraneous quotes.
    """
    if text1 is None or text2 is None:
        return False
    # Clean the texts before comparison.
    text1 = clean_text(text1)
    text2 = clean_text(text2)
    similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
    return similarity >= threshold


def cluster_subtitles(rows, similarity_threshold=0.8):
    """
    Clusters consecutive subtitle frames if their texts are similar.

    Parameters:
      rows: List of dictionaries (each row from the TSV)
      similarity_threshold: Similarity threshold (0 to 1) for clustering

    Returns:
      List of clusters. Each cluster is a dict with:
        - 'text': Representative subtitle text (cleaned)
        - 'start_time': Start time (in ms) of the cluster
        - 'end_time': End time (in ms) of the cluster
        - 'frames': List of rows that belong to the cluster
    """
    clusters = []
    current_cluster = None

    # Ensure rows are sorted by time.
    sorted_rows = sorted(rows, key=lambda x: x["time"])

    for row in sorted_rows:
        raw_text = row.get("text")
        text = clean_text(raw_text)
        time = row.get("time")

        # Skip invalid text (None, "none", "nan", or empty strings)
        if text is None or text.lower() in ["none", "nan", ""]:
            if current_cluster is not None:
                clusters.append(current_cluster)
                current_cluster = None
            continue

        # Start a new cluster if none is active.
        if current_cluster is None:
            current_cluster = {
                "text": text,
                "text_list": [text],
                "start_time": time,
                "end_time": time,
                "frames": [row],
            }
        else:
            # If the current row's text is similar to the current cluster's text, update the cluster.
            if is_similar(
                current_cluster["text"], text, threshold=similarity_threshold
            ):
                current_cluster["end_time"] = time
                current_cluster["text_list"].append(text)
                current_cluster["frames"].append(row)
            else:
                clusters.append(current_cluster)
                current_cluster = {
                    "text": text,
                    "text_list": [text],
                    "start_time": time,
                    "end_time": time,
                    "frames": [row],
                }

    if current_cluster is not None:
        clusters.append(current_cluster)

    return clusters


# Example usage:
file_path = "subtitles.tsv"
rows = read_tsv(file_path)
clusters = cluster_subtitles(rows, similarity_threshold=0.8)


def ms_to_srt_time(ms):
    """
    Converts a millisecond value to SRT time format (HH:MM:SS,mmm).
    """
    hours = ms // (3600 * 1000)
    minutes = (ms % (3600 * 1000)) // (60 * 1000)
    seconds = (ms % (60 * 1000)) // 1000
    milliseconds = ms % 1000
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def frame_to_ms(frame, fps):
    return int(frame * 1000 / fps)


def clusters_to_srt(clusters):
    """
    Converts subtitle clusters to a single SRT-formatted string.

    Each cluster becomes one SRT entry.
    """
    srt_entries = []
    for i, cluster in enumerate(clusters, start=1):
        start = ms_to_srt_time(cluster["start_time"])

        unit_ms = frame_to_ms(1, 25)
        real_end_time = cluster["end_time"] + unit_ms
        end = ms_to_srt_time(real_end_time)

        # text = cluster["text"]
        # find the most common text in the cluster
        text = max(cluster["text_list"], key=cluster["text_list"].count)

        srt_entry = f"{i}\n{start} --> {end}\n{text}\n"
        srt_entries.append(srt_entry)
    return "\n".join(srt_entries)


# Example usage:
srt_output = clusters_to_srt(clusters)
with open("output.srt", "w", encoding="utf-8") as f:
    f.write(srt_output)
