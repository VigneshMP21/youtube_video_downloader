# 🎬 YouTube Video & Shorts Downloader (Python)

A simple, fast, and powerful Python tool to download YouTube videos and Shorts in the **highest available quality** (4K, 2K, 1080p, 60fps, HDR) with automatic audio merging and resume support for **long videos** (podcasts, documentaries, and streams).

---

## 📌 Prerequisites (First Time Setup)

Before running the program, ensure you have **Python 3.8 or higher** installed on your computer.

1. **Check if Python is installed:**
   Open your Terminal (Command Prompt / PowerShell on Windows, or Terminal on Mac/Linux) and type:
   ```bash
   python --version
   ```
   *(If `python` is not recognized, try `python3 --version`).*

2. **If Python is NOT installed:**
   - Download and install it from the official website: [python.org/downloads](https://www.python.org/downloads/)
   - ⚠️ **Important (Windows users):** During installation, make sure to check the box:
     **☑ "Add python.exe to PATH"**

---

## 🚀 Step-by-Step Execution Guide (For First-Time Users)

Follow these simple steps to run the downloader:

### Step 1: Open the Project Folder in Terminal

- **Windows:**
  1. Open this folder in **File Explorer**.
  2. Click on the address bar at the top of the file explorer window.
  3. Type `cmd` and press **Enter**. A command prompt window will open directly in this folder.
  
  *(Alternative on Windows/Mac/VS Code: Right-click inside the folder and select "Open in Terminal" or "Open with VS Code").*

- **Mac / Linux:**
  Open Terminal and navigate to this folder:
  ```bash
  cd path/to/youtube_video_downloader
  ```

---

### Step 2: Install Required Dependencies

Install the required packages by running this command in your terminal:

```bash
pip install -r requirements.txt
```
*(On Mac/Linux, if needed, run `pip3 install -r requirements.txt`).*

> **Note:** The requirements automatically set up `yt-dlp` and portable `imageio-ffmpeg`. You do **not** need to install or configure FFmpeg separately!

---

### Step 3: Run the Program

Start the interactive downloader:

```bash
python downloader.py
```
*(Or `python3 downloader.py` on Mac/Linux).*

You will see the main menu on your screen:

```text
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
Enter choice (0-5) [default 1]:
```

---

### Step 4: Download a Video or Short

1. Press **Enter** (to select option 1 - Highest Quality).
2. **Copy** your YouTube link from your web browser or phone.
   - Standard video example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - YouTube Short example: `https://www.youtube.com/shorts/3jz_24qZ8E4`
3. **Paste** the link into the terminal and press **Enter**.
4. Watch the live progress bar:
   ```text
   [*] Fetching video details...
   Title   : Me at the zoo
   Channel : jawed
   Duration: 00:19 (19s)
   ----------------------------------------------------------------------
   [*] Mode: HIGHEST QUALITY (Best Video + Best Audio)
   [*] Starting download... (resume-enabled)
   [██████████████████████████████] 100.0% | 218 KB / 218 KB | 1.47 MB/s | ETA: 00:00
   [✓] Download stream completed. Merging video & audio...
   [SUCCESS] Download completed in 00:06!
   ```

---

### Step 5: Find Your Downloaded Video

All downloaded videos and shorts are automatically saved inside the **`downloads/`** folder in this project directory:
```text
youtube_video_downloader/
│
├── downloads/                     <--- YOUR DOWNLOADED VIDEOS ARE HERE!
│   └── Video Title [VIDEO_ID].mp4
├── downloader.py
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Command-Line Usage (Optional / Advanced)

If you don't want to use the interactive menu, you can also pass links directly via command line:

### 1. Download in Highest Quality directly:
```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Download a YouTube Short:
```bash
python downloader.py "https://www.youtube.com/shorts/SHORT_ID"
```

### 3. Download Audio Only (High-Bitrate MP3):
```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" -q audio
```

### 4. Limit Quality to 1080p or 720p:
```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" -q 1080p
```

### 5. Custom Download Folder:
```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "D:/MyVideos"
```

### 6. Batch Download Multiple Videos at Once:
Create a text file called `links.txt` with one URL per line:
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

## 💡 Key Highlights

- **Handles Long Videos (1h, 3h, 10h+)**: Built with concurrent fragment downloading for fast speeds and timeout guards.
- **Auto-Resume**: If your internet disconnects midway through a large video, just run the command again with the same link — it resumes from where it stopped instead of starting from 0%.
- **True Highest Quality**: Downloads separate high-bitrate video (e.g. 4K/1080p) and audio streams and merges them cleanly into `.mp4` using FFmpeg.
- **Zero Complex Setup**: FFmpeg is automatically resolved by the script.

---

## ❓ Troubleshooting & FAQs

- **Q: `'python'` or `'pip'` is not recognized as an internal or external command?**  
  *Fix:* Make sure Python is added to your system PATH. Re-run the Python installer, choose "Modify", and check "Add Python to environment variables / PATH".

- **Q: How do I pause or stop a download?**  
  *Fix:* Press `Ctrl + C` in your terminal. Re-running the link later will automatically resume where it was interrupted.

- **Q: Can I download private or age-restricted videos?**  
  *Fix:* The downloader works on all public and unlisted YouTube videos and Shorts.
