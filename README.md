# FFmpeg-based MP3 Splitter

This tool splits large MP3 files into smaller segments based on silence detection using FFmpeg. It can handle files of any size without memory limitations, making it perfect for large OST files that would exceed the 4GB limit of other solutions.

## Key Features

- ✅ **No file size limits** - Can process files larger than 4GB
- ✅ **Memory efficient** - Uses FFmpeg's native processing
- ✅ **Fast processing** - No need to load entire file into memory
- ✅ **High quality** - Uses FFmpeg's copy mode (no re-encoding)
- ✅ **Robust silence detection** - FFmpeg's built-in silencedetect filter

## Requirements

- Python 3.6+
- FFmpeg (system dependency)

## Installation

### Install FFmpeg:
- **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## Usage

### One-click installation and run (Windows):
```bash
install_and_run.bat "your_file.mp3"
```
*Automatically installs FFmpeg if needed and runs the splitter*


### Command Line (Recommended):
```bash
python split_ost.py "your_file.mp3"
```

### With custom parameters:
```bash
python split_ost.py "your_file.mp3" -o output_folder -t -48 -d 1.5
```

### Auto-detection mode:
```bash
python split_large_mp3.py
```

### Windows Batch File:
Double-click `quick_run.bat` for automatic processing.

## Parameters

- `input_file`: Path to the MP3 file to split
- `-o, --output`: Output directory (default: "splits")
- `-t, --threshold`: Silence threshold in dB (default: -48)
- `-d, --duration`: Minimum silence duration in seconds (default: 1.5)

## How It Works

1. **Detection Phase**: Uses FFmpeg's `silencedetect` filter to analyze the entire file and identify silence periods
2. **Parsing Phase**: Extracts silence timestamps and converts them to non-silent segments
3. **Splitting Phase**: Uses FFmpeg's segment extraction with copy mode (no re-encoding)

## Example Output

```
FFmpeg-based MP3 Splitter
Processing: Clair Obscur： Expedition 33 (Original Soundtrack) Full OST [LAQZfeETFbg].mp3
File size: 2.34 GB
Duration: 7234.56 seconds (120.58 minutes)
Sample rate: 44100 Hz
Channels: 2
Codec: mp3

Detecting silence using FFmpeg...
Threshold: -48dB, Min duration: 1.5s
Found 45 silence periods

Splitting audio into 46 segments...
Extracting track 01: Clair_Obscur_Expedition_33_OST_track_01.mp3 (234.56s)
  ✓ Saved: 0.00s - 234.56s
...

============================================================
Splitting complete!
Original duration: 7234.56s
Segments duration: 7198.23s
Files created: 46 tracks in 'splits' directory
============================================================
```

## Technical Advantages

- **No file size limitations** - Handles files larger than 4GB efficiently
- **Minimal memory usage** - Processes files without loading into RAM
- **Fast processing** - Native FFmpeg performance
- **Lossless quality** - Uses copy mode (no re-encoding)
- **Simple dependencies** - Only requires FFmpeg (no Python audio libraries)

## Troubleshooting

### "FFmpeg not found" error:
- Ensure FFmpeg is installed and added to your system PATH
- Test with: `ffmpeg -version`

### No segments detected:
- Try a lower threshold (more negative): `-t -60`
- Try shorter minimum duration: `-d 1.0`

### Very short segments:
- Segments shorter than 5 seconds are automatically filtered out
- Adjust the threshold or duration parameters