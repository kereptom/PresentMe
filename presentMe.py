from PIL import Image
from moviepy.editor import VideoFileClip
import cv2
import pandas as pd
import numpy as np
import argparse
import subprocess
from pydub import AudioSegment
import os
import shutil
from pydub.utils import mediainfo


def blend_frames(frame1, frame2, alpha):
    return cv2.addWeighted(frame1, 1-alpha, frame2, alpha, 0)

# Function to extract audio from video using ffmpeg
def extract_audio_from_video(video_path, audio_path):
    subprocess.run(['ffmpeg', '-y', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path])


# Function to generate silence audio of given duration
def generate_silence(duration, output_path):
    subprocess.run(
        ['ffmpeg', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo:d={duration}', '-q:a', '0', output_path])


# Function to resize image to Full HD
def resize_image_to_full_hd(image_path):
    with Image.open(image_path) as img:
        img = img.resize((1920, 1080))
        img_array = np.array(img)
    return img_array


# Function to overlay webcam on the slide
def overlay_webcam(slide, webcam_path, new_position, new_size):
    webcam_video = VideoFileClip(webcam_path)
    for frame in webcam_video.iter_frames(fps=25, dtype='uint8'):
        slide_copy = slide.copy()
        webcam_small = cv2.resize(frame, new_size)
        slide_copy[new_position[1]:new_position[1] + new_size[1],
        new_position[0]:new_position[0] + new_size[0]] = webcam_small
        yield cv2.cvtColor(slide_copy, cv2.COLOR_BGR2RGB)


# Function to overlay and blend webcams on the slide
def overlay_and_blend_webcams(last_full_slide, next_webcam_first_frame, new_position, new_size, fps):
    # Initialize an array to hold the blended frames
    blended_frames = []

    # Resize the first frame of the next webcam
    next_webcam_small = cv2.cvtColor(cv2.resize(next_webcam_first_frame, new_size), cv2.COLOR_BGR2RGB)

    for alpha in np.linspace(0, 1, fps):
        # Create a copy of the last full slide
        slide_copy = last_full_slide.copy()

        # Blend the webcam frames
        blended_webcam = cv2.addWeighted(
            last_full_slide[new_position[1]:new_position[1] + new_size[1],
            new_position[0]:new_position[0] + new_size[0]],
            1 - alpha,
            next_webcam_small,
            alpha,
            0
        )

        # Overlay the blended webcam onto the slide
        slide_copy[new_position[1]:new_position[1] + new_size[1],
        new_position[0]:new_position[0] + new_size[0]] = blended_webcam

        # Add the blended frame to the list
        blended_frames.append(slide_copy)

    return blended_frames


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a conference presentation video.")
    parser.add_argument("-s", "--slides", required=True, help="Folder containing slide images.")
    parser.add_argument("-w", "--webcams", required=True, help="Folder containing webcam videos.")
    parser.add_argument("-t", "--outline", required=True, help="Text file outlining the slide and webcam mapping.")
    parser.add_argument("-o", "--output", required=True, help="Output video file name.")
    parser.add_argument("-a", "--audio", required=True, help="Output audio file name.")

    args = parser.parse_args()
    webcams_folder = args.webcams
    setup_file = args.outline
    output_audio_file = args.audio
    slide_webcam_list = pd.read_csv(args.outline, sep=' ', names=['slide', 'webcam_or_duration'])

    temp_video_files = []
    temp_audio_files = []
    temp_merged_files = []
    next_webcam_first_frame = None

    # Audio Operations
    for video_file in os.listdir(webcams_folder):
        if video_file.endswith(".mp4"):
            video_path = os.path.join(webcams_folder, video_file)
            audio_path = os.path.join(webcams_folder, video_file.replace('.mp4', '.mp3'))
            extract_audio_from_video(video_path, audio_path)

    for index, row in slide_webcam_list.iterrows():
        slide_path = os.path.join(args.slides, row['slide'])
        webcam_path_or_duration = row['webcam_or_duration']

        try:
            webcam_path_or_duration = float(webcam_path_or_duration)
        except ValueError:
            pass

        slide = resize_image_to_full_hd(slide_path)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        temp_output_video_file = os.path.join(args.webcams, f"slide{index + 1}_temp_video.mp4")
        temp_output_audio_file = os.path.join(args.webcams, f"slide{index + 1}_temp_audio.mp3")
        out = cv2.VideoWriter(temp_output_video_file, fourcc, 25.0, (1920, 1080))

        if isinstance(webcam_path_or_duration, (int, float)):
            for _ in range(int(25 * webcam_path_or_duration)):
                out.write(cv2.cvtColor(slide, cv2.COLOR_BGR2RGB))
            generate_silence(webcam_path_or_duration, temp_output_audio_file)
        else:
            webcam_path = os.path.join(args.webcams, webcam_path_or_duration)
            audio_path = os.path.join(args.webcams, webcam_path_or_duration.replace('.mp4', '.mp3'))
            shutil.copy(audio_path, temp_output_audio_file)

            # Load existing audio and append 1 second of silence
            current_audio = AudioSegment.from_file(temp_output_audio_file, format="mp3")
            one_sec_silence = AudioSegment.silent(duration=1000)  # 1 second of silence
            new_audio = current_audio + one_sec_silence
            new_audio.export(temp_output_audio_file, format="mp3")

            new_position = (1565, 847)
            new_size = (318, 181)
            last_frame = None  # Variable to hold the last frame
            for frame in overlay_webcam(slide, webcam_path, new_position, new_size):
                out.write(frame)
                last_frame = frame  # Update the last frame
            if index + 1 < len(slide_webcam_list):
                next_row = slide_webcam_list.iloc[index + 1]
                next_webcam_path_or_duration = next_row['webcam_or_duration']
                if not isinstance(next_webcam_path_or_duration, (int, float)):
                    next_webcam_path = os.path.join(args.webcams, next_webcam_path_or_duration)
                    next_webcam_first_frame = next(VideoFileClip(next_webcam_path).iter_frames())
            # Example usage in your main loop
            if last_frame is not None and next_webcam_first_frame is not None:
                fps = 25  # Assuming 25 FPS
                blended_frames = overlay_and_blend_webcams(last_frame, next_webcam_first_frame, new_position, new_size,
                                                           fps)
                for blended_frame in blended_frames:
                    out.write(blended_frame)

        out.release()
        temp_video_files.append(temp_output_video_file)
        temp_audio_files.append(temp_output_audio_file)

        # Merge the audio and video for this slide
        temp_merged_file = os.path.join(args.webcams, f"slide{index + 1}_temp_merged.mp4")
        subprocess.run([
            'ffmpeg', '-y',
            '-i', temp_output_video_file,
            '-i', temp_output_audio_file,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-ac', '1',
            temp_merged_file
        ])

        temp_merged_files.append(temp_merged_file)

    # Step 1: Create a text file with the list of temporary merged video files
    with open("concat_list.txt", "w") as f:
        for temp_merged_file in temp_merged_files:
            f.write(f"file '{temp_merged_file}'\n")

    # Step 2: Concatenate all temporary merged slide videos to form the final video
    subprocess.run([
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'concat_list.txt',
        '-c', 'copy',
        args.output
    ])

    # Remove temporary video and audio files
    for temp_file in temp_video_files:
        os.remove(temp_file)
    for temp_file in temp_audio_files:
        os.remove(temp_file)
