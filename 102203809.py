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
            print(f"Error downloading video {i + 1}: {e}")
    
    return video_files

def convert_videos_to_audio(video_files):
    audio_files = []
    for video_file in video_files:
        try:
            #I encountered many errors in this function and ChatGPT suggested a try block, code for which was partly AI generated
            # Convert video to audio using ffmpeg
            video_clip = VideoFileClip(video_file)
            audio_filename = video_file.replace(".webm", ".mp3")
            
            # Export audio from the video file
            video_clip.audio.write_audiofile(audio_filename)
            audio_files.append(audio_filename)
            print(f"Converted {video_file} to audio: {audio_filename}")
        
        except Exception as e:
            print(f"Error converting {video_file} to audio file: {e}")
    
    return audio_files


def trim_audio_files(audio_files, duration):
    trimmed_files = []
    for audio_file in audio_files:
        try:
            audio = AudioSegment.from_mp3(audio_file)
            trimmed_audio = audio[:duration * 1000]  #milliseconds
            trimmed_filename = f"trimmed_{audio_file}"
            trimmed_audio.export(trimmed_filename, format="mp3")
            trimmed_files.append(trimmed_filename)
            print(f"Trimmed {audio_file} to {duration} seconds")
        except CouldntDecodeError:
            print(f"Couldn't decode this {audio_file}, skipping.")
        except Exception as e:
            print(f"Error while trimming {audio_file}: {e}")
    
    return trimmed_files

def merge_audios(trimmed_files, output_filename):
    if len(trimmed_files) == 0:
        print("No audios to merge.")
        return

    try:
        #This try block was also suggested during debugging through AI, code written by self
        combined = AudioSegment.from_mp3(trimmed_files[0])
        for audio_file in trimmed_files[1:]:
            audio = AudioSegment.from_mp3(audio_file)
            combined += audio
        
        combined.export(output_filename, format="mp3")
        print(f"Merged audio is saved as {output_filename} in the root folder")
    except Exception as e:
        print(f"Error merging the audio files: {e}")

def main():
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        return

    singer_name = sys.argv[1]
    try:
        number_of_videos = int(sys.argv[2])
        audio_duration = int(sys.argv[3])
        output_filename = sys.argv[4]
        
        if number_of_videos <= 10 or audio_duration <= 15:
            print("Number of videos must be greater than 10 and audio duration must be greater than 15 seconds to accomodate for the integrity of the mashup. In my opinion any mashup smaller than 2 minutes 30 seconds is no mashup at all.")
            return
    except ValueError:
        print("Number of videos and audio duration should be integers.")
        return

    # Download videos
    video_files = download_videos(singer_name, number_of_videos)
    
    # Convert videos to audio
    audio_files = convert_videos_to_audio(video_files)
    
    # Trim audio files
    trimmed_files = trim_audio_files(audio_files, audio_duration)
    
    # Merge trimmed audio files
    merge_audios(trimmed_files, output_filename)

if __name__ == "__main__":
    main()
