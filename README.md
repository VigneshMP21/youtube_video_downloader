# YouTube Video & Shorts Downloader (Python)

A powerful, reliable, and user-friendly Python program to download YouTube videos and YouTube Shorts in the **highest available quality** (4K, 2K, 1080p, 60fps, HDR) with dedicated optimizations for **long videos** (podcasts, documentaries, lectures, and live stream replays).

---

## Key Features

1. **Highest Quality Video & Audio**:
   - Automatically downloads the highest video stream (4K/2K/1080p60) and combines it with the highest quality audio stream.
   - Automatically merges them into a clean, universally playable `.mp4` file via FFmpeg.
   
2. **Optimized for Long Videos**:
   - **Auto-Resume**: If your connection drops or you stop the download midway, re-running the script will automatically resume from where it stopped instead of starting over.
   - **Multi-threaded Fragment Downloads**: Downloads video chunks concurrently for significantly higher speeds on long videos.
   - **Connection Drop Protection**: Built with aggressive network retries (20 retries on fragment drop) and socket timeout guards to avoid indefinite hanging.
   - **Real-time Live Progress Bar**: Shows percentage, downloaded size, total size, download speed, and ETA.

3. **YouTube Shorts & Regular Videos**:
   - Supports any YouTube URL format:
     - Standard: `https://www.youtube.com/watch?v=VIDEO_ID`
     - Shortened: `https://youtu.be/VIDEO_ID`
     - Shorts: `https://www.youtube.com/shorts/VIDEO_ID`

4. **Self-Healing FFmpeg Integration**:
   - Automatically detects FFmpeg in your system PATH or utilizes `imageio-ffmpeg` directly, so you don't have to manually configure environment variables.

5. **Two Execution Modes**:
   - **Interactive Menu**: Run `python downloader.py` and simply paste your link.
   - **Command Line (CLI)**: Automate or pass links directly as arguments.
   - **Batch Download**: Download multiple videos at once from a `.txt` file.

---

## Installation

Ensure you have Python installed, then install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Interactive Mode (Easiest)
Run the script without arguments:
```bash
python downloader.py
```
You will be greeted with an interactive menu:
```
======================================================================
        YOUTUBE VIDEOS & SHORTS DOWNLOADER (HIGHEST QUALITY)        
======================================================================
  1. Download Single Video or Short (Highest Quality - Default)
  2. Download Video with Quality Selection (1080p, 720p, etc.)
  3. Download Audio Only (High-Bitrate MP3)
  4. Batch Download from Text File (list of links)
  5. Change Output Folder
  0. Exit
----------------------------------------------------------------------
```

### 2. Quick Command-Line Mode
Download any video or short directly in the highest quality:
```bash
# Standard video
python downloader.py "https://www.youtube.com/watch?v=EXAMPLE_ID"

# YouTube Short
python downloader.py "https://www.youtube.com/shorts/EXAMPLE_ID"
```

### 3. Specify Quality Target
```bash
# Up to 1080p
python downloader.py "https://www.youtube.com/watch?v=EXAMPLE_ID" -q 1080p

# Audio only (MP3)
python downloader.py "https://www.youtube.com/watch?v=EXAMPLE_ID" -q audio
```

### 4. Custom Output Directory
```bash
python downloader.py "https://www.youtube.com/watch?v=EXAMPLE_ID" -o "D:/MyVideos"
```

### 5. Batch Download from a Text File
Create a text file (e.g. `links.txt`) with one URL per line:
```text
https://www.youtube.com/watch?v=video1
https://www.youtube.com/shorts/short1
https://www.youtube.com/watch?v=video2
```
Then run:
```bash
python downloader.py -b links.txt
```

---

## Notes
- Downloaded videos are saved to the `downloads/` folder by default.
- If you interrupt a long video download (using `Ctrl+C`), running the command again will automatically resume the partial download!
