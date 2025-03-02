from utils.constants import VIDEO_META, VIDEO_PATH

import yt_dlp
import os


yt_opts = {
    "verbose": True,
    "cookiesfrombrowser": ("chrome",),  # Use Chrome cookies
}

# Get working directory, yt-dlp will download files to this directory
cwd = os.getcwd()
print(f"Script executing from: {cwd}")


for video_meta in VIDEO_META:
    print(f"Downloading episode {video_meta.episode_number}")
    video_path = video_meta.local_path

    if os.path.exists(video_path):
        print(f"The video was already downloaded")
        continue

    # files before download
    files_before = os.listdir(cwd)
    print(f"Files before download: {files_before}")

    with yt_dlp.YoutubeDL(yt_opts) as ydl:
        ydl.download(video_meta.youtube_url)

    # files after download
    files_after = os.listdir(cwd)
    print(f"Files after download: {files_after}")

    # get the new file
    new_files = [
        f for f in files_after if f not in files_before and f.endswith(".webm")
    ]

    if len(new_files) == 0:
        print(f"The video was already downloaded")
        continue
    elif len(new_files) > 1:
        raise ValueError(f"Expected 1 new file, got {len(new_files)}")
    else:
        new_file = new_files[0]

    print(f"New file: {new_file}")

    # move the new file to the video directory
    print(f"Moving {new_file} to {video_path}")
    os.rename(new_file, video_path)
