# SRT Video Check Tool

This tool helps you check and edit SRT subtitle files against video files. It allows you to visualize subtitle bounding boxes, edit subtitles, and navigate between them easily.

## Features

- Select episodes from the video metadata
- Display videos with dimmed regions except for the subtitle bounding box
- See current subtitle text displayed below the video with subtitle-style formatting
- Adjust video brightness and contrast with collapsible controls
- Drag & drop SRT files for editing
- Edit subtitle text inline
- Navigate between subtitles using up/down arrow keys
- Delete subtitles using Cmd+Backspace (Mac) or Ctrl+Backspace (Windows/Linux)
- Jump to subtitle timestamps in the video
- Delete unwanted subtitle entries
- Save edited SRT files
- Clean interface with toggleable panels for video adjustments
- Vertical layout with video at the top, subtitle editor in the middle, and file drop area at the bottom

## How to Use

### Setting Up

1. **Run with a local server**: Due to browser security restrictions, this tool needs to be served from a web server when accessing local video files. You can use one of these methods:

   - Python simple server:
     ```
     cd /path/to/wlwz-scripts
     python -m http.server
     ```
     Then open: http://localhost:8000/srt-video-check/
   - Node.js with http-server:
     ```
     npm install -g http-server
     cd /path/to/wlwz-scripts
     http-server
     ```
     Then open: http://localhost:8080/srt-video-check/

2. **CORS issues**: If you encounter CORS issues, make sure your server is configured to allow access to local files.

3. **Path handling**: The tool automatically adjusts video paths from `./video/...` (as specified in the JSON) to `../video/...` when running from the `srt-video-check` directory. No need to modify the original JSON file.

### Using the Tool

1. Select an episode from the dropdown menu
2. Drag and drop an SRT file onto the designated area at the bottom (or use the file input)
3. The video will load and the subtitle area will be highlighted
4. The current subtitle text will appear below the video with white text and black outline
5. To adjust video visibility:
   - Click the "Video Adjustments" button below the video
   - Use the brightness and contrast sliders as needed
   - Click the button again to hide the controls when done
6. Navigate between subtitles using:
   - Up/down arrow keys (↑/↓)
   - The "Previous Subtitle" and "Next Subtitle" buttons
7. Edit subtitle text directly in the text area
   - Changes to the text will immediately update the subtitle preview below the video
8. Delete subtitles using:
   - The × button on the subtitle card
   - Cmd+Backspace (Mac) or Ctrl+Backspace (Windows/Linux) for the current subtitle
9. Click "Save SRT" to download the edited file

### Video Controls

Below the video player, you'll find a toggle button for video adjustment controls:

- Click "Video Adjustments" to reveal or hide the control panel
- **Brightness slider**: Adjust from 50% to 200% (default is 100%)
- **Contrast slider**: Adjust from 50% to 200% (default is 100%)
- **Reset button**: Quickly return both settings to their default values

These controls are particularly helpful when working with videos that are too dark or have low contrast, making subtitle placement difficult to see.

### Subtitle Preview

Between the video and controls, you'll see a subtitle preview area that:
- Shows the currently selected subtitle text
- Formats text in white with a black outline, similar to standard video subtitles
- Updates in real-time as you edit the subtitle text
- Helps visualize how the subtitle will appear on the video

### Layout

The tool features a vertical layout with:
- Video player at the top of the screen
- Subtitle preview display showing the current subtitle text
- Collapsible video controls for brightness and contrast
- Subtitle controls and horizontally scrollable subtitle cards in the middle
- File drop area at the bottom for loading new SRT files
- Automatic scrolling to the current subtitle when navigating

This design provides a more traditional video player layout with subtitles displayed below the video, and keeps the file loading interface separate from the editing area.

## Troubleshooting

- **Video doesn't play**: Make sure the video file paths in `video_meta.json` are correct relative to the project root. The tool will automatically adjust "./video/" paths to "../video/" when needed.
- **Metadata doesn't load**: Check that the path to `video_meta.json` is correct. The tool tries both `../video/video_meta.json` and `./video/video_meta.json`.
- **Subtitle box position is wrong**: Verify that the bounding box coordinates in `video_meta.json` are correct for your videos. 