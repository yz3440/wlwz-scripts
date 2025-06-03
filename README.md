# 武林外传 Script Project (wlwz-script)

An open source effort to create a clean, structured, and timestamped version of the complete script for **武林外传** (My Own Swordsman), one of China's most beloved sitcoms.

## Project Overview

This project combines community-transcribed scripts with OCR-extracted subtitles from official video sources to create the most accurate and comprehensive digital archive of 武林外传's dialogue, complete with timestamps, speaker attribution, and emotional context.

### Key Features

- **Complete Script Archive**: All 80 episodes with cleaned and standardized dialogue
- **Precise Timestamps**: Frame-accurate timing through OCR subtitle extraction
- **Speaker Attribution**: Character identification and emotional context
- **Quality Assurance**: Multi-stage validation and manual auditing process

## 📁 Project Structure

```
wlwz-script/
├── content-source/          # Original source materials
│   ├── 《武林外传》全剧本.pdf    # Community-transcribed script (PDF)
│   ├── 《武林外传》全剧本.txt    # Plain text conversion
│   └── community-scripts-audited.txt # Consistency-edited version
├── content-output/          # Processed and structured data
│   └── episodes/           # Per-episode JSON files
├── src/                    # Processing pipeline scripts
├── subtitle-cluster/       # Subtitle processing tools
├── srt-video-check/       # Subtitle quality assurance tools
└── video/                 # Downloaded video files (gitignored)
```

## 🔄 Processing Pipeline

### Phase A: Script Processing

1. **`a1_extract_scripts.py`** - Extract individual episode scripts from source text
2. **`a2_parse_scene_scripts.py`** - Parse scripts into scene-based structure
3. **`a3_ensure_character_consistency.py`** - Standardize character names and references
4. **`a99_consolidate_parsed_all_scripts.py`** - Consolidate all processed scripts

### Phase B: Subtitle Extraction

1. **`b1_download_episode_video.py`** - Download episodes from YouTube (CCTV 电视剧 channel)
2. **`b2_ocr_subtitles.py`** - Extract subtitles through OCR of every frame

### Phase C: Integration

1. **`c1_consolidate_parsed_scripts.py`** - Prepare scripts for subtitle matching
2. **`c2_match_episode_scripts_with_subtitles.py`** - Match scripts with extracted subtitles

### Subtitle Processing

- **`subtitle-cluster/1_cluster.py`** - Group and organize subtitle segments
- **`subtitle-cluster/2_clean_up_srt.py`** - Clean and standardize subtitle format

## Technology Stack

- **Python 3.x** - Primary processing language
- **OpenCV** - Video frame processing
- **OCRmac** - macOS native OCR for subtitle extraction
- **Anthropic API** - LLM assistance for script structuring
- **yt-dlp** - YouTube video downloading
- **JSON Schema** - Data validation and structure enforcement

## Data Sources

### Script Source

- **Primary**: Community-transcribed scripts from Baidu Tieba (2007)
- **Contributors**: 30+ dedicated fans who transcribed from official DVDs
- **Coverage**: Complete 80-episode series
- **Format**: PDF → TXT → Scene-based JSON

### Video Source

- **Platform**: YouTube (CCTV 电视剧 official channel)
- **Processing**: Frame-by-frame OCR extraction for canonical text and timing

## Output Format

Each episode is processed into a paired output format:

### 1. Script with IDs (`script_w_id.json`)

Structured JSON containing dialogue with scene and line identifiers:

```json
{
  "episode": 1,
  "scenes": [
    {
      "sceneNumber": 1,
      "type": "normal",
      "rawDescription": "【门口，夜】",
      "location": "门口",
      "timeOfDay": "夜",
      "performances": [
        {
          "type": "action",
          "description": "\"同福客栈\"匾额特写，镜头下拉，到大门口"
        },
        {
          "type": "action",
          "description": "老邢从大门出来，掌柜跟出"
        },
        {
          "type": "dialog",
          "speaker": "邢育森",
          "performances": [
            {
              "type": "line",
              "line": "我得走~",
              "lineId": "ep1-s1-l1",
              "textToMatch": "我得走"
            }
          ]
        },
        ...
    }
  ]
}
```

### 2. Subtitles with IDs (`subtitles_with_id.srt`)

Standard SRT format with cross-referenced line identifiers:

```srt
1
00:01:29,079 --> 00:01:29,840
我得走 [ep1-s1-l1]

2
00:01:30,200 --> 00:01:30,920
老邢 [ep1-s1-l2]
```

This paired format allows for:

- **Canonical timestamps** from OCR-extracted subtitles
- **Rich context** from community-transcribed scripts
- **Cross-referencing** between script content and precise timing
- **Flexible usage** for different applications (subtitles, analysis, etc.)

## Copyright & Legal

This project is created for educational and archival purposes only.

- **Original Content**: All rights to "武林外传" belong to Beijing Union Film Company (北京联盟影业公司)
- **Community Scripts**: Created by fans in 2007 for personal enjoyment
- **Usage**: Non-commercial use only
- **Distribution**: Educational and research purposes

## Acknowledgments

- **Original Script Contributors**: 30+ Baidu Tieba community members (2007)
- **Video Source**: CCTV 电视剧 YouTube channel
- **Technical Inspiration**: Modern NLP and OCR technologies
- **Community**: 武林外传 fans worldwide

## Project Status

- ✅ Script extraction and parsing
- ✅ Video downloading pipeline
- ✅ OCR subtitle extraction
- 🔄 Script-subtitle matching (in progress)
- 📋 Quality assurance and validation (planned)
- 📋 Final JSON output generation (planned)
