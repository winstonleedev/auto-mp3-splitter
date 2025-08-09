#!/usr/bin/env python3
"""
FFmpeg-based MP3 splitter for large audio files
Uses FFmpeg for efficient silence detection and splitting without memory limitations
"""

import os
import sys
import subprocess
import json
import re
import argparse
from pathlib import Path

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_audio_info(input_file):
    """Get audio file information using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        
        # Extract relevant information
        format_info = info['format']
        audio_stream = next(s for s in info['streams'] if s['codec_type'] == 'audio')
        
        duration = float(format_info['duration'])
        size = int(format_info['size'])
        
        return {
            'duration': duration,
            'size': size,
            'sample_rate': int(audio_stream['sample_rate']),
            'channels': int(audio_stream['channels']),
            'codec': audio_stream['codec_name']
        }
    except Exception as e:
        print(f"Error getting audio info: {e}")
        return None

def detect_silence_ffmpeg(input_file, silence_thresh=-48, min_silence_duration=1.5):
    """
    Use FFmpeg's silencedetect filter to find silence periods
    Returns list of (start, end) tuples for non-silent segments
    """
    print(f"Detecting silence using FFmpeg...")
    print(f"Threshold: {silence_thresh}dB, Min duration: {min_silence_duration}s")
    
    # FFmpeg silencedetect command
    cmd = [
        'ffmpeg', '-i', input_file, '-af', 
        f'silencedetect=noise={silence_thresh}dB:d={min_silence_duration}',
        '-f', 'null', '-'
    ]
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stderr
        
        # Parse silence detection output
        silence_starts = []
        silence_ends = []
        
        # Find silence start and end times
        for line in output.split('\n'):
            if 'silence_start:' in line:
                match = re.search(r'silence_start: ([\d.]+)', line)
                if match:
                    silence_starts.append(float(match.group(1)))
            elif 'silence_end:' in line:
                match = re.search(r'silence_end: ([\d.]+)', line)
                if match:
                    silence_ends.append(float(match.group(1)))
        
        print(f"Found {len(silence_starts)} silence periods")
        
        # Convert silence periods to non-silent segments
        non_silent_segments = []
        
        # Get total duration
        info = get_audio_info(input_file)
        if not info:
            return []
        
        total_duration = info['duration']
        
        # Build non-silent segments
        current_start = 0.0
        
        for i in range(len(silence_starts)):
            if i < len(silence_ends):
                # Non-silent segment before this silence
                silence_start = silence_starts[i]
                silence_end = silence_ends[i]
                
                if silence_start > current_start:
                    non_silent_segments.append((current_start, silence_start))
                
                current_start = silence_end
        
        # Add final segment if there's audio after the last silence
        if current_start < total_duration:
            non_silent_segments.append((current_start, total_duration))
        
        # Filter out very short segments (less than 5 seconds)
        non_silent_segments = [(start, end) for start, end in non_silent_segments 
                              if end - start >= 5.0]
        
        return non_silent_segments
        
    except Exception as e:
        print(f"Error during silence detection: {e}")
        return []

def split_audio_ffmpeg(input_file, segments, output_dir, base_name):
    """
    Split audio file using FFmpeg based on detected segments
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    print(f"\nSplitting audio into {len(segments)} segments...")
    
    for i, (start_time, end_time) in enumerate(segments):
        duration = end_time - start_time
        output_filename = f"{base_name}_track_{i+1:02d}.mp3"
        output_path = os.path.join(output_dir, output_filename)
        
        # FFmpeg command to extract segment
        cmd = [
            'ffmpeg', '-i', input_file,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',  # Copy without re-encoding for speed
            '-avoid_negative_ts', 'make_zero',
            '-y',  # Overwrite output files
            output_path
        ]
        
        try:
            print(f"Extracting track {i+1:2d}: {output_filename} ({duration:.2f}s)")
            subprocess.run(cmd, capture_output=True, check=True)
            print(f"  ✓ Saved: {start_time:.2f}s - {end_time:.2f}s")
            
        except subprocess.CalledProcessError as e:
            print(f"  ✗ Error extracting segment {i+1}: {e}")

def split_mp3_file(input_file, output_dir=None, silence_thresh=-48, min_silence_duration=1.5):
    """
    Main function to split MP3 file using FFmpeg
    """
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        return False
    
    if not check_ffmpeg():
        print("Error: FFmpeg not found. Please install FFmpeg:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt-get install ffmpeg")
        return False
    
    # Get file info
    print(f"Processing: {input_file}")
    info = get_audio_info(input_file)
    if not info:
        return False
    
    print(f"File size: {info['size'] / (1024*1024*1024):.2f} GB")
    print(f"Duration: {info['duration']:.2f} seconds ({info['duration']/60:.2f} minutes)")
    print(f"Sample rate: {info['sample_rate']} Hz")
    print(f"Channels: {info['channels']}")
    print(f"Codec: {info['codec']}")
    
    # Set up output directory and base name
    if output_dir is None:
        output_dir = "splits"
    
    base_name = Path(input_file).stem
    # Clean up base name for file system compatibility
    base_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
    
    # Detect silence and get segments
    segments = detect_silence_ffmpeg(input_file, silence_thresh, min_silence_duration)
    
    if not segments:
        print("No segments detected. Try adjusting the silence threshold or duration.")
        return False
    
    # Split the audio
    split_audio_ffmpeg(input_file, segments, output_dir, base_name)
    
    # Summary
    total_segments_duration = sum(end - start for start, end in segments)
    print(f"\n{'='*60}")
    print(f"Splitting complete!")
    print(f"Original duration: {info['duration']:.2f}s")
    print(f"Segments duration: {total_segments_duration:.2f}s")
    print(f"Files created: {len(segments)} tracks in '{output_dir}' directory")
    print(f"{'='*60}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Split MP3 files using FFmpeg-based silence detection")
    parser.add_argument("input_file", help="Path to input MP3 file")
    parser.add_argument("-o", "--output", help="Output directory (default: splits)")
    parser.add_argument("-t", "--threshold", type=int, default=-48, 
                       help="Silence threshold in dB (default: -48)")
    parser.add_argument("-d", "--duration", type=float, default=1.5,
                       help="Minimum silence duration in seconds (default: 1.5)")
    
    args = parser.parse_args()
    
    print("FFmpeg-based MP3 Splitter")
    print("Handles large files efficiently without memory limitations")
    print("-" * 60)
    
    success = split_mp3_file(
        args.input_file,
        args.output,
        args.threshold,
        args.duration
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()