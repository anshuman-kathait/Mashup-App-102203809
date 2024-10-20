import tkinter as tk
from tkinter import messagebox
import sys
import os
from yt_dlp import YoutubeDL
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from pydub.exceptions import CouldntDecodeError

def download_videos(singer_name, number_of_videos):
    ydl_opts = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': f'{singer_name}_video_%(autonumber)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }

    video_files = []
    search_url = f"ytsearch{number_of_videos}:{singer_name}"
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(search_url, download=False)
            for i, video in enumerate(search_results['entries']):
                print(f"Downloading video {i+1}: {video['title']}")
                video_info = ydl.extract_info(video['webpage_url'], download=True)
                filename = ydl.prepare_filename(video_info)
                video_files.append(filename)
                print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Error donloading video {i + 1}: {e}")
    
    return video_files

def convert_videos_to_audio(video_files):
    audio_files = []
    for video_file in video_files:
        try:
            video_clip = VideoFileClip(video_file)
            audio_filename = video_file.replace(".webm", ".mp3")
            video_clip.audio.write_audiofile(audio_filename)
            audio_files.append(audio_filename)
            print(f"Converted {video_file} to audio: {audio_filename}")
        except Exception as e:
            print(f"Error convertig {video_file} to audio: {e}")
    
    return audio_files

def trim_audio_files(audio_files, duration):
    trimmed_files = []
    for audio_file in audio_files:
        try:
            audio = AudioSegment.from_mp3(audio_file)
            trimmed_audio = audio[:duration * 1000]
            trimmed_filename = f"trimmed_{audio_file}"
            trimmed_audio.export(trimmed_filename, format="mp3")
            trimmed_files.append(trimmed_filename)
            print(f"Trimmed {audio_file} to {duration} seconds")
        except CouldntDecodeError:
            print(f"Couldn't decode {audio_file}, skipping.")
        except Exception as e:
            print(f"Eror trimming {audio_file}: {e}")
    
    return trimmed_files

def merge_audios(trimmed_files, output_filename):
    if len(trimmed_files) == 0:
        print("No audio files t0 merge.")
        return

    try:
        combined = AudioSegment.from_mp3(trimmed_files[0])
        for audio_file in trimmed_files[1:]:
            audio = AudioSegment.from_mp3(audio_file)
            combined += audio
        
        combined.export(output_filename, format="mp3")
        print(f"Merged audio saved as {output_filename}")
    except Exception as e:
        print(f"Error mergng audio files: {e}")

def run_program():
    singer_name = singer_name_entry.get()
    number_of_videos = number_of_videos_entry.get()
    audio_duration = audio_duration_entry.get()
    output_filename = output_filename_entry.get()

    try:
        number_of_videos = int(number_of_videos)
        audio_duration = int(audio_duration)

        if number_of_videos <= 10 or audio_duration <= 15:
            messagebox.showerror("Input Error", "Number of videos must be greater than 10 and audio duration must be greater than 15 seconds. Refer to last program as to why.")
            return

        # Download videos
        video_files = download_videos(singer_name, number_of_videos)
        
        # Convert videos to audio
        audio_files = convert_videos_to_audio(video_files)
        
        # Trim audio files
        trimmed_files = trim_audio_files(audio_files, audio_duration)
        
        # Merge trimmed audio files
        merge_audios(trimmed_files, output_filename)
        
        messagebox.showinfo("Success", "Process completed successfully!")

    except ValueError:
        messagebox.showerror("Input Error", "Number of videos and audio duration must be integers.")

# Create main window
root = tk.Tk()
root.title("YouTube Audio Mashup")

#input fields
tk.Label(root, text="Singer Name:").grid(row=0, column=0, padx=10, pady=10)
singer_name_entry = tk.Entry(root)
singer_name_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Number of Vids:").grid(row=1, column=0, padx=10, pady=10)
number_of_videos_entry = tk.Entry(root)
number_of_videos_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Audio Duration (seconds):").grid(row=2, column=0, padx=10, pady=10)
audio_duration_entry = tk.Entry(root)
audio_duration_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Output Filename:").grid(row=3, column=0, padx=10, pady=10)
output_filename_entry = tk.Entry(root)
output_filename_entry.grid(row=3, column=1, padx=10, pady=10)

#Run
run_button = tk.Button(root, text="Run", command=run_program)
run_button.grid(row=4, columnspan=2, pady=20)

# Start GUI loop
root.mainloop()
