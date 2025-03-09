document.addEventListener('DOMContentLoaded', () => {
  // DOM elements
  const episodeSelect = document.getElementById('episode-select');
  const videoWrapper = document.getElementById('video-wrapper');
  const videoPlayer = document.getElementById('video-player');
  const currentSubtitleDisplay = document.getElementById(
    'current-subtitle-display'
  );
  const currentSubtitleText = document.getElementById('current-subtitle-text');
  const videoControlsToggle = document.getElementById('video-controls-toggle');
  const videoControlsContainer = document.getElementById(
    'video-controls-container'
  );
  const videoControls = document.getElementById('video-controls');
  const brightnessSlider = document.getElementById('brightness-slider');
  const contrastSlider = document.getElementById('contrast-slider');
  const brightnessValue = document.getElementById('brightness-value');
  const contrastValue = document.getElementById('contrast-value');
  const resetVideoFilters = document.getElementById('reset-video-filters');
  const dimmedOverlay = document.getElementById('dimmed-overlay');
  const subtitleBox = document.getElementById('subtitle-box');
  const srtDropArea = document.getElementById('srt-drop-area');
  const srtFileInput = document.getElementById('srt-file-input');
  const srtControls = document.getElementById('srt-controls');
  const srtEditor = document.getElementById('srt-editor');
  const prevSubtitleBtn = document.getElementById('prev-subtitle');
  const nextSubtitleBtn = document.getElementById('next-subtitle');
  const saveSrtBtn = document.getElementById('save-srt');

  // State
  let videoMetadata = [];
  let currentEpisode = null;
  let subtitles = [];
  let currentSubtitleIndex = -1;

  // Load video metadata
  fetch('../video/video_meta.json')
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      videoMetadata = data;
      populateEpisodeSelector(data);
    })
    .catch((error) => {
      console.error('Error loading video metadata:', error);

      // Try with alternate path as fallback
      fetch('./video/video_meta.json')
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          videoMetadata = data;
          populateEpisodeSelector(data);
        })
        .catch((fallbackError) => {
          console.error(
            'Error loading video metadata (fallback):',
            fallbackError
          );
          alert(
            'Failed to load video metadata. Please check the console for details.'
          );
        });
    });

  // Video controls toggle functionality
  videoControlsToggle.addEventListener('click', () => {
    const isExpanded = videoControlsToggle.classList.toggle('expanded');

    if (isExpanded) {
      videoControlsContainer.classList.add('expanded');
    } else {
      videoControlsContainer.classList.remove('expanded');
    }
  });

  // Populate episode selector
  function populateEpisodeSelector(episodes) {
    episodes.forEach((episode) => {
      const option = document.createElement('option');
      option.value = episode.episode_number;
      option.textContent = `Episode ${episode.episode_number}`;
      episodeSelect.appendChild(option);
    });
  }

  // Event: Episode selection
  episodeSelect.addEventListener('change', () => {
    const episodeNumber = episodeSelect.value;
    if (!episodeNumber) {
      videoWrapper.classList.add('hidden');
      videoControlsToggle.classList.add('hidden');
      currentSubtitleDisplay.classList.add('hidden');
      return;
    }

    currentEpisode = videoMetadata.find(
      (ep) => ep.episode_number === episodeNumber
    );
    if (currentEpisode) {
      loadVideo(currentEpisode);
      videoControlsToggle.classList.remove('hidden');
    }
  });

  // Video filter functionality
  function updateVideoFilters() {
    const brightness = brightnessSlider.value;
    const contrast = contrastSlider.value;

    brightnessValue.textContent = `${brightness}%`;
    contrastValue.textContent = `${contrast}%`;

    videoPlayer.style.filter = `brightness(${brightness}%) contrast(${contrast}%)`;
  }

  brightnessSlider.addEventListener('input', updateVideoFilters);
  contrastSlider.addEventListener('input', updateVideoFilters);

  resetVideoFilters.addEventListener('click', () => {
    brightnessSlider.value = 100;
    contrastSlider.value = 100;
    updateVideoFilters();
  });

  // Load video and set up bounding boxes
  function loadVideo(episode) {
    // Adjust the video path to account for the directory difference
    let videoPath = episode.local_path;

    // If the path is relative and starts with "./video/", adjust it to "../video/"
    if (videoPath.startsWith('./video/')) {
      videoPath = videoPath.replace('./video/', '../video/');
    }

    videoPlayer.src = videoPath;
    videoPlayer.width = episode.width;
    videoPlayer.height = episode.height;

    // Set up subtitle bounding box
    const { x, y, w, h } = episode.subtitle_boundingbox;
    subtitleBox.style.left = `${x}px`;
    subtitleBox.style.top = `${y}px`;
    subtitleBox.style.width = `${w}px`;
    subtitleBox.style.height = `${h}px`;

    // Create hole in the dimmed overlay for subtitle area
    dimmedOverlay.style.clipPath = `polygon(
            0% 0%, 100% 0%, 100% 100%, 0% 100%, 
            0% ${y}px, ${x}px ${y}px, 
            ${x}px ${y + h}px, ${x + w}px ${y + h}px, 
            ${x + w}px ${y}px, 0% ${y}px
        )`;

    videoWrapper.classList.remove('hidden');
    videoControlsToggle.classList.remove('hidden');

    // Reset video filters when loading a new video
    brightnessSlider.value = 100;
    contrastSlider.value = 100;
    updateVideoFilters();

    // Collapse video controls by default
    videoControlsToggle.classList.remove('expanded');
    videoControlsContainer.classList.remove('expanded');
  }

  // SRT parsing functions
  function parseSRT(content) {
    // First normalize line endings and trim the content
    const normalizedContent = content
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .trim();

    // Use a more robust regex that handles multiple consecutive newlines
    // This will split on one or more empty lines
    const blocks = normalizedContent.split(/\n{2,}/);
    const parsed = [];

    blocks.forEach((block) => {
      // Skip empty blocks
      if (!block.trim()) return;

      const lines = block.split(/\n/);
      // Ensure we have at least 2 lines (index and timecode)
      if (lines.length >= 2) {
        // Try to parse the index as an integer
        const indexLine = lines[0].trim();
        let index;
        try {
          index = parseInt(indexLine);
          if (isNaN(index)) throw new Error('Invalid index');
        } catch (e) {
          console.warn(`Skipping block with invalid index: ${indexLine}`);
          return;
        }

        // Look for a line containing the timecode separator ' --> '
        let timecodeLineIndex = -1;
        for (let i = 1; i < lines.length; i++) {
          if (lines[i].includes(' --> ')) {
            timecodeLineIndex = i;
            break;
          }
        }

        // If no valid timecode line was found, skip this block
        if (timecodeLineIndex === -1) {
          console.warn(`Skipping block ${index}: No valid timecode found`);
          return;
        }

        const timecodes = lines[timecodeLineIndex].trim();
        const text = lines.slice(timecodeLineIndex + 1).join('\n');

        try {
          const [startTime, endTime] = parseTimecodes(timecodes);

          parsed.push({
            index,
            startTime,
            endTime,
            text,
            timecodes,
          });
        } catch (e) {
          console.warn(
            `Skipping block ${index} due to timecode parsing error: ${e.message}`
          );
        }
      }
    });

    return parsed;
  }

  function parseTimecodes(timecode) {
    const parts = timecode.split(' --> ');
    if (parts.length !== 2) {
      throw new Error(`Invalid timecode format: ${timecode}`);
    }
    return [timeToSeconds(parts[0]), timeToSeconds(parts[1])];
  }

  function timeToSeconds(timeString) {
    if (!timeString) {
      throw new Error('Empty timestring');
    }

    const parts = timeString.split(',');
    if (parts.length !== 2) {
      throw new Error(
        `Invalid time format (missing milliseconds): ${timeString}`
      );
    }

    const [time, milliseconds] = parts;
    const [hours, minutes, seconds] = time.split(':').map(Number);

    if (
      isNaN(hours) ||
      isNaN(minutes) ||
      isNaN(seconds) ||
      isNaN(parseInt(milliseconds))
    ) {
      throw new Error(`Invalid time components in: ${timeString}`);
    }

    return (
      hours * 3600 + minutes * 60 + seconds + parseInt(milliseconds) / 1000
    );
  }

  function secondsToTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds - Math.floor(seconds)) * 1000);

    return `${h.toString().padStart(2, '0')}:${m
      .toString()
      .padStart(2, '0')}:${s.toString().padStart(2, '0')},${ms
      .toString()
      .padStart(3, '0')}`;
  }

  // Handle SRT file drop
  srtDropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    srtDropArea.classList.add('dragover');
  });

  srtDropArea.addEventListener('dragleave', () => {
    srtDropArea.classList.remove('dragover');
  });

  srtDropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    srtDropArea.classList.remove('dragover');

    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.srt')) {
      loadSRTFile(file);
    } else {
      alert('Please drop a valid .srt file');
    }
  });

  srtFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      loadSRTFile(file);
    }
  });

  function loadSRTFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target.result;
      subtitles = parseSRT(content);
      if (subtitles.length > 0) {
        renderSubtitles();
        srtControls.classList.remove('hidden');
        srtEditor.classList.remove('hidden');
        setCurrentSubtitle(0);
        currentSubtitleDisplay.classList.remove('hidden');
      } else {
        alert('No subtitles found in the file');
      }
    };
    reader.readAsText(file);
  }

  // Render subtitles in the editor
  function renderSubtitles() {
    srtEditor.innerHTML = '';

    subtitles.forEach((subtitle, index) => {
      const entry = document.createElement('div');
      entry.className = 'srt-entry';
      entry.dataset.index = index;

      const header = document.createElement('div');
      header.className = 'srt-header';
      header.textContent = `#${subtitle.index} (${secondsToTime(
        subtitle.startTime
      )})`;

      // Create delete button
      const deleteBtn = document.createElement('button');
      deleteBtn.className = 'delete-btn';
      deleteBtn.innerHTML = '&times;'; // × symbol
      deleteBtn.title = 'Delete this subtitle';
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent triggering the entry click event
        deleteSubtitle(index);
      });

      const entryHeader = document.createElement('div');
      entryHeader.className = 'entry-header';
      entryHeader.appendChild(header);
      entryHeader.appendChild(deleteBtn);

      const textArea = document.createElement('textarea');
      textArea.className = 'srt-text';
      textArea.value = subtitle.text;
      textArea.rows = 3;
      textArea.addEventListener('change', (e) => {
        subtitles[index].text = e.target.value;

        // Update the display if this is the current subtitle
        if (index === currentSubtitleIndex) {
          currentSubtitleText.textContent = e.target.value;
        }
      });

      entry.appendChild(entryHeader);
      entry.appendChild(textArea);

      entry.addEventListener('click', () => {
        setCurrentSubtitle(index);
      });

      srtEditor.appendChild(entry);
    });
  }

  // Delete a subtitle entry
  function deleteSubtitle(index) {
    // Ask for confirmation
    if (
      confirm(
        `Are you sure you want to delete subtitle #${subtitles[index].index}?`
      )
    ) {
      // Remove the subtitle from the array
      subtitles.splice(index, 1);

      // Re-render the subtitles
      renderSubtitles();

      // Update the current subtitle index
      if (currentSubtitleIndex >= subtitles.length) {
        currentSubtitleIndex = subtitles.length - 1;
      }

      // If there are still subtitles, set the current one
      if (subtitles.length > 0 && currentSubtitleIndex >= 0) {
        setCurrentSubtitle(currentSubtitleIndex);
      } else if (subtitles.length === 0) {
        // If all subtitles were deleted, hide the editor and controls
        srtEditor.classList.add('hidden');
        srtControls.classList.add('hidden');
        alert('All subtitles have been deleted.');
      }
    }
  }

  // Set the current subtitle and update UI
  function setCurrentSubtitle(index) {
    if (index < 0 || index >= subtitles.length) {
      return;
    }

    // Update state
    currentSubtitleIndex = index;

    // Update UI
    const entries = srtEditor.querySelectorAll('.srt-entry');
    entries.forEach((entry) => {
      entry.classList.remove('active');
    });

    const currentEntry = entries[index];
    currentEntry.classList.add('active');

    // Calculate scroll position to center the entry
    // Get container dimensions
    const containerWidth = srtEditor.clientWidth;
    const entryWidth = currentEntry.offsetWidth;
    const entryLeft = currentEntry.offsetLeft;

    // Calculate the scroll position that centers the entry
    const scrollPosition = entryLeft - containerWidth / 2 + entryWidth / 2;

    // Instant scroll to position (no smooth scrolling)
    srtEditor.scrollTo({
      left: Math.max(0, scrollPosition),
      behavior: 'auto', // Changed from 'smooth' to 'auto' for instant scrolling
    });

    // Update subtitle display
    currentSubtitleText.textContent = subtitles[index].text;
    currentSubtitleDisplay.classList.remove('hidden');

    // Focus the text area
    const textArea = currentEntry.querySelector('.srt-text');
    if (textArea) {
      textArea.focus();
    }

    // Seek video to the middle point between the start and end time of the subtitle
    if (videoPlayer.readyState >= 2) {
      const startTime = subtitles[index].startTime;
      const endTime = subtitles[index].endTime;
      const middleTime = startTime + (endTime - startTime) / 2;
      videoPlayer.currentTime = middleTime;
      videoPlayer.pause();
    }
  }

  // Event: Navigate between subtitles
  prevSubtitleBtn.addEventListener('click', () => {
    setCurrentSubtitle(currentSubtitleIndex - 1);
  });

  nextSubtitleBtn.addEventListener('click', () => {
    setCurrentSubtitle(currentSubtitleIndex + 1);
  });

  // Keyboard navigation - changed to up/down arrows
  document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowUp') {
      setCurrentSubtitle(currentSubtitleIndex - 1);
    } else if (e.key === 'ArrowDown') {
      setCurrentSubtitle(currentSubtitleIndex + 1);
    } else if (
      e.key === 'Backspace' &&
      (e.metaKey || e.ctrlKey) &&
      currentSubtitleIndex >= 0
    ) {
      // Prevent the default browser behavior for Cmd/Ctrl+Backspace
      e.preventDefault();

      // Delete the currently focused subtitle entry
      deleteSubtitle(currentSubtitleIndex);
    }
  });

  // Save edited SRT
  saveSrtBtn.addEventListener('click', () => {
    const srtContent = generateSRT();
    downloadSRT(srtContent);
  });

  function generateSRT() {
    let content = '';

    subtitles.forEach((subtitle, i) => {
      const startTime = secondsToTime(subtitle.startTime);
      const endTime = secondsToTime(subtitle.endTime);

      content += `${i + 1}\n`;
      content += `${startTime} --> ${endTime}\n`;
      content += `${subtitle.text}\n\n`;
    });

    return content;
  }

  function downloadSRT(content) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'edited_subtitles.srt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
});
