from utils.constants import VIDEO_META, get_output_episode_path
import cv2
import os
from ocrmac import ocrmac
from PIL import Image


SAVE_FRAMES_FLAG = 1  # 0: no frames, 1: every frame with subtitles, 2: every frame
FRAME_STEP = 1  # sample every single frame


def extract_subtitles(video_path: str, output_dir: str, x: int, y: int, w: int, h: int):
    video_file_name = os.path.splitext(os.path.basename(video_path))[0]
    print(f"Extracting subtitles for {video_file_name}")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(os.path.join(output_dir, "frames")):
        os.makedirs(os.path.join(output_dir, "frames"))

    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0
    success = True

    subtitles = []

    def log_subtitle(frame_count, subtitle, confidence, timestamp):
        subtitles.append(
            {
                "frame": frame_count,
                "text": subtitle,
                "confidence": confidence,
                "time": timestamp,
            }
        )

    # Calculate total frames and set frame position
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        success, frame = cap.read()
        if not success:
            break

        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))  # Get timestamp in milliseconds

        if frame_count % FRAME_STEP == 0:
            # Crop selected region
            roi = frame[y : y + h, x : x + w]

            # convert cv2 image to PIL image
            pil_image = Image.fromarray(roi)

            annotations = ocrmac.OCR(
                pil_image,
                language_preference=["zh-Hans", "en-US"],
                recognition_level="accurate",
            ).recognize()

            annotation_count = len(annotations)
            if annotation_count == 0:
                # Delete the frame
                log_subtitle(frame_count, None, None, timestamp)
                print(f"Frame {frame_count}: ")

            else:
                # 2 annotations are the subtitle and the timestamp
                text = []
                for annotation in annotations:
                    text.append(annotation[0])

                confidence = 0
                for annotation in annotations:
                    confidence += annotation[1]
                confidence /= annotation_count

                text = " ".join(text)
                print(f"Frame {frame_count}: {text} ({confidence*100:.2f}%)")
                log_subtitle(frame_count, text, confidence, timestamp)

            if SAVE_FRAMES_FLAG > 0:
                os.makedirs(os.path.join(output_dir, "frames"), exist_ok=True)
                output_frame_path = os.path.join(
                    output_dir, "frames", f"frame_{saved_count}_f{frame_count}.png"
                )
                if SAVE_FRAMES_FLAG == 1:
                    if annotation_count > 0:
                        cv2.imwrite(
                            output_frame_path,
                            roi,
                            [int(cv2.IMWRITE_PNG_COMPRESSION), 9],
                        )
                elif SAVE_FRAMES_FLAG == 2:
                    cv2.imwrite(
                        output_frame_path, roi, [int(cv2.IMWRITE_PNG_COMPRESSION), 9]
                    )

            # Save subtitles to file
            with open(os.path.join(output_dir, "subtitles_wip.tsv"), "w") as f:
                f.write("frame\ttext\tconfidence\ttime\n")
                for subtitle in subtitles:
                    f.write(
                        f"{subtitle['frame']}\t{subtitle['text']}\t{subtitle['confidence']}\t{subtitle['time']}\n"
                    )

            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Extracted and filtered {saved_count} frames.")

    # Rename subtitles_wip.tsv to subtitles.tsv
    os.remove(os.path.join(output_dir, "subtitles_wip.tsv"))

    with open(os.path.join(output_dir, "subtitles.tsv"), "w") as f:
        f.write("frame\ttext\tconfidence\ttime\n")
        for subtitle in subtitles:
            f.write(
                f"{subtitle['frame']}\t{subtitle['text']}\t{subtitle['confidence']}\t{subtitle['time']}\n"
            )


for video_meta in VIDEO_META:
    print(f"Extracting subtitles for episode {video_meta.episode_number}")
    output_dir = get_output_episode_path(video_meta.episode_number)
    video_path = video_meta.local_path

    if os.path.exists(os.path.join(output_dir, "subtitles.tsv")):
        print(f"Subtitles already extracted for episode {video_meta.episode_number}")
        continue

    extract_subtitles(
        video_path=video_path,
        output_dir=output_dir,
        x=video_meta.subtitle_boundingbox.x,
        y=video_meta.subtitle_boundingbox.y,
        w=video_meta.subtitle_boundingbox.w,
        h=video_meta.subtitle_boundingbox.h,
    )
