#!/usr/bin/env python3
"""
YouTube Video & Shorts Downloader
---------------------------------
Features:
- Downloads YouTube videos and Shorts in the HIGHEST available quality (4K, 2K, 1080p, 60fps, HDR).
- Handles long videos (multi-hour podcasts, streams, documentaries) with resume support,
  multi-threaded fragment downloading, and aggressive connection retries.
- Automatically handles video + audio merging via FFmpeg.
- Supports both interactive console mode and CLI command-line arguments.
- Supports batch downloads (multiple URLs or text file list).
- Optional audio-only extraction (MP3/M4A).
"""

import sys
import os
import re
import time
import shutil
import argparse
from typing import Optional, Dict, Any

try:
    import yt_dlp
except ImportError:
    print("[ERROR] 'yt-dlp' is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)


# ==============================================================================
# FFmpeg & Environment Setup Helper
# ==============================================================================

def find_or_setup_ffmpeg() -> Optional[str]:
    """
    Locates FFmpeg on the system, checks PATH, or automatically utilizes
    imageio-ffmpeg if installed so the user never gets FFmpeg errors.
    """
    # 1. Check if ffmpeg is in PATH
    ffmpeg_in_path = shutil.which("ffmpeg")
    if ffmpeg_in_path:
        return os.path.dirname(ffmpeg_in_path)

    # 2. Try to get FFmpeg from imageio_ffmpeg
    try:
        import imageio_ffmpeg
        exe_path = imageio_ffmpeg.get_ffmpeg_exe()
        bin_dir = os.path.dirname(exe_path)

        # yt-dlp expects 'ffmpeg.exe' inside the directory on Windows
        standard_ffmpeg_exe = os.path.join(bin_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if not os.path.exists(standard_ffmpeg_exe) and os.path.exists(exe_path):
            try:
                shutil.copy2(exe_path, standard_ffmpeg_exe)
            except Exception:
                pass

        if os.path.exists(standard_ffmpeg_exe):
            return bin_dir
        elif os.path.exists(exe_path):
            return exe_path
    except ImportError:
        pass

    # 3. Check common Windows installation paths
    common_paths = [
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
    ]
    for p in common_paths:
        candidate = os.path.join(p, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        if os.path.exists(candidate):
            return p

    return None


def get_js_runtimes_config() -> Dict[str, Any]:
    """
    Detects available JavaScript runtimes (Node.js, Deno, Bun, QuickJS)
    to allow yt-dlp to bypass YouTube signature/bot challenges easily.
    """
    for rt in ["node", "deno", "bun", "quickjs"]:
        if shutil.which(rt):
            return {rt: {}}
    return {}


# ==============================================================================
# Progress and Status Hook
# ==============================================================================

def format_bytes(byte_count: Optional[float]) -> str:
    """Format bytes into human-readable B, KB, MB, GB."""
    if byte_count is None or byte_count <= 0:
        return "Unknown size"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if byte_count < 1024.0:
            return f"{byte_count:.2f} {unit}"
        byte_count /= 1024.0
    return f"{byte_count:.2f} PB"


def format_seconds(seconds: Optional[float]) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


class DownloadProgressHook:
    """Provides a clean, unified progress bar in the terminal."""

    def __init__(self):
        self.last_update = 0.0

    def __call__(self, d: Dict[str, Any]):
        status = d.get("status")
        if status == "downloading":
            now = time.time()
            # Throttle terminal redraws to ~10 times a second to prevent terminal lag on fast connections
            if now - self.last_update < 0.1 and d.get("downloaded_bytes") != d.get("total_bytes"):
                return
            self.last_update = now

            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed")
            eta = d.get("eta")

            percent_str = f"{(downloaded / total * 100):.1f}%" if total else "N/A"
            speed_str = f"{format_bytes(speed)}/s" if speed else "-- KB/s"
            downloaded_str = format_bytes(downloaded)
            total_str = format_bytes(total) if total else "Unknown"
            eta_str = format_seconds(eta) if eta is not None else "--:--"

            # Progress bar visualization (30 blocks wide)
            bar_len = 30
            if total and total > 0:
                filled = int(bar_len * downloaded / total)
                bar = "█" * filled + "░" * (bar_len - filled)
            else:
                bar = "▒" * bar_len

            sys.stdout.write(
                f"\r  [{bar}] {percent_str:>6} | {downloaded_str} / {total_str} | {speed_str:>12} | ETA: {eta_str} "
            )
            sys.stdout.flush()

        elif status == "finished":
            sys.stdout.write("\n  [✓] Download stream completed. Merging video & audio...\n")
            sys.stdout.flush()


# ==============================================================================
# Core Downloader Engine
# ==============================================================================

class YouTubeDownloader:
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.ffmpeg_location = find_or_setup_ffmpeg()
        self.js_runtimes = get_js_runtimes_config()

    def get_base_options(self) -> Dict[str, Any]:
        """
        Builds optimized yt-dlp configuration:
        - Highest quality video + highest quality audio merge
        - Resuming capability for long videos
        - Connection retries & timeouts
        - Multi-threaded fragment downloading
        """
        opts: Dict[str, Any] = {
            # Destination template
            "outtmpl": os.path.join(self.output_dir, "%(title)s [%(id)s].%(ext)s"),
            # Restrict filenames to avoid Windows path issues
            "windowsfilenames": True,
            "restrictfilenames": False,
            # Long Video Robustness:
            # - Resume interrupted downloads
            # - Multi-retries on connection drops
            # - 30s socket timeout
            "continuedl": True,
            "retries": 20,
            "fragment_retries": 20,
            "file_access_retries": 10,
            "socket_timeout": 30,
            # Download multiple fragments concurrently for high-speed HLS/DASH streams (great for long videos)
            "concurrent_fragment_downloads": 5,
            "buffersize": 1024 * 64,
            # Audio / Video merging
            "merge_output_format": "mp4",
            # JS runtime to handle signature challenges & prevent format limitations
            "js_runtimes": self.js_runtimes,
            "remote_components": ["ejs:github"],
            # Progress reporting
            "progress_hooks": [DownloadProgressHook()],
            "quiet": True,
            "no_warnings": False,
        }

        if self.ffmpeg_location:
            opts["ffmpeg_location"] = self.ffmpeg_location

        return opts

    def get_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch video metadata without downloading."""
        opts = {
            "quiet": True,
            "extract_flat": False,
            "ffmpeg_location": self.ffmpeg_location,
            "js_runtimes": self.js_runtimes,
            "remote_components": ["ejs:github"],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            try:
                return ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"[!] Error fetching video details: {e}")
                return None

    def download(self, url: str, quality_mode: str = "highest") -> bool:
        """
        Downloads the video/short based on selected quality mode.

        quality_mode:
          - 'highest': Best available video stream (4K/1440p/1080p) + Best audio stream, merged to MP4/MKV.
          - '1080p': Best video up to 1080p + Best audio.
          - '720p': Best video up to 720p + Best audio.
          - 'audio': Best audio only, extracted as MP3.
        """
        # Validate URL
        url = url.strip()
        if not url:
            print("[!] Empty URL provided.")
            return False

        # Identify if this is a Shorts URL or standard video
        is_short = "/shorts/" in url
        video_kind = "YouTube Short" if is_short else "YouTube Video"

        print("\n" + "=" * 70)
        print(f"  Target: {video_kind}")
        print(f"  URL   : {url}")
        print("=" * 70)

        # 1. Inspect Video Info First
        print("  [*] Fetching video details...")
        info = self.get_info(url)
        if not info:
            print("[!] Could not retrieve video information. Please check the URL or your internet connection.")
            return False

        title = info.get("title", "Unknown Title")
        duration = info.get("duration", 0)
        channel = info.get("uploader", "Unknown Channel")
        views = info.get("view_count", 0)

        duration_formatted = format_seconds(duration)
        print(f"  Title   : {title}")
        print(f"  Channel : {channel}")
        print(f"  Duration: {duration_formatted} ({duration}s)")
        if views:
            print(f"  Views   : {views:,}")
        print("-" * 70)

        # 2. Configure Format Selection
        ydl_opts = self.get_base_options()

        if quality_mode == "highest":
            # Downloads the absolute highest resolution available (8K, 4K, 1440p, 1080p60) + highest audio
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"
            print("  [*] Mode: HIGHEST QUALITY (Best Video + Best Audio)")
        elif quality_mode == "1080p":
            ydl_opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"
            print("  [*] Mode: Up to 1080p Full HD")
        elif quality_mode == "720p":
            ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"
            print("  [*] Mode: Up to 720p HD")
        elif quality_mode == "audio":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }]
            print("  [*] Mode: AUDIO ONLY (Highest Quality 320kbps MP3)")
        else:
            ydl_opts["format"] = "bestvideo+bestaudio/best"

        # 3. Download
        print(f"  [*] Output Folder: {self.output_dir}")
        print("  [*] Starting download... (resume-enabled)")
        start_time = time.time()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            elapsed = time.time() - start_time
            print("\n" + "=" * 70)
            print(f"  [SUCCESS] Download completed in {format_seconds(elapsed)}!")
            print(f"  [SAVED TO] {self.output_dir}")
            print("=" * 70 + "\n")
            return True

        except KeyboardInterrupt:
            print("\n\n[!] Download paused/cancelled by user. (You can resume anytime by re-running with this link!)")
            return False
        except Exception as e:
            print(f"\n[!] Download failed: {e}")
            return False


# ==============================================================================
# Interactive CLI & Batch Runner
# ==============================================================================

def interactive_menu(downloader: YouTubeDownloader):
    """Interactive loop for user-friendly operation."""
    while True:
        print("\n" + "=" * 70)
        print("        YOUTUBE VIDEOS & SHORTS DOWNLOADER (HIGHEST QUALITY)        ")
        print("=" * 70)
        print("  1. Download Single Video or Short (Highest Quality - Default)")
        print("  2. Download Video with Quality Selection (1080p, 720p, etc.)")
        print("  3. Download Audio Only (High-Bitrate MP3)")
        print("  4. Batch Download from Text File (list of links)")
        print("  5. Change Output Folder")
        print("  0. Exit")
        print("-" * 70)

        choice = input("Enter choice (0-5) [default 1]: ").strip()
        if not choice:
            choice = "1"

        if choice == "0":
            print("\nGoodbye!")
            break

        elif choice == "1":
            url = input("\nPaste YouTube Video or Short link: ").strip()
            if url:
                downloader.download(url, quality_mode="highest")
            else:
                print("[!] No link provided.")

        elif choice == "2":
            url = input("\nPaste YouTube Video or Short link: ").strip()
            if not url:
                print("[!] No link provided.")
                continue

            print("\nSelect Quality Target:")
            print("  [1] Highest Available (4K / 2K / 1080p 60fps)")
            print("  [2] 1080p Full HD")
            print("  [3] 720p HD")
            q_choice = input("Enter quality (1-3) [default 1]: ").strip()
            q_map = {"1": "highest", "2": "1080p", "3": "720p"}
            downloader.download(url, quality_mode=q_map.get(q_choice, "highest"))

        elif choice == "3":
            url = input("\nPaste YouTube link: ").strip()
            if url:
                downloader.download(url, quality_mode="audio")
            else:
                print("[!] No link provided.")

        elif choice == "4":
            file_path = input("\nEnter path to .txt file containing links (one per line): ").strip().strip('"\'')
            if not os.path.exists(file_path):
                print(f"[!] File not found: {file_path}")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            print(f"\n[*] Found {len(urls)} link(s) to download.")
            for idx, url in enumerate(urls, 1):
                print(f"\n--- Item {idx}/{len(urls)} ---")
                downloader.download(url, quality_mode="highest")

        elif choice == "5":
            new_dir = input(f"\nCurrent folder: {downloader.output_dir}\nEnter new download folder path: ").strip()
            if new_dir:
                downloader.output_dir = os.path.abspath(new_dir)
                os.makedirs(downloader.output_dir, exist_ok=True)
                print(f"[✓] Output directory updated to: {downloader.output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube Videos and Shorts in Highest Quality with long video support."
    )
    parser.add_argument("url", nargs="?", help="YouTube video or Short URL")
    parser.add_argument(
        "-q", "--quality",
        choices=["highest", "1080p", "720p", "audio"],
        default="highest",
        help="Download quality (default: highest)"
    )
    parser.add_argument(
        "-o", "--output",
        default="downloads",
        help="Output directory (default: 'downloads')"
    )
    parser.add_argument(
        "-b", "--batch",
        help="Text file containing links to batch download (one URL per line)"
    )

    args = parser.parse_args()
    downloader = YouTubeDownloader(output_dir=args.output)

    # 1. Batch mode from CLI
    if args.batch:
        if not os.path.exists(args.batch):
            print(f"[!] File not found: {args.batch}")
            sys.exit(1)
        with open(args.batch, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"[*] Batch downloading {len(urls)} URLs...")
        for url in urls:
            downloader.download(url, quality_mode=args.quality)
        return

    # 2. Single URL from CLI
    if args.url:
        downloader.download(args.url, quality_mode=args.quality)
        return

    # 3. No arguments -> Launch Interactive Menu
    interactive_menu(downloader)


if __name__ == "__main__":
    main()
