import ffmpeg
import os

# Add known ffmpeg path to environment
ffmpeg_path = r"C:\Users\sathv\anaconda3\envs\seci\Library\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + ffmpeg_path

def extract_audio(video_path, output_audio="audio.wav"):
    """
    Extract high-quality audio from video and format it for speech recognition.
    
    Parameters:
        video_path (str): Path to input video file
        output_audio (str): Path to output audio file

    Returns:
        str: Path to extracted audio file
    """

    try:
        (
            ffmpeg
            .input(video_path)
            .output(
                output_audio,
                acodec='pcm_s16le',
                ac=1,                
                ar='16000'           
            )
            .run(overwrite_output=True)
        )

        print("Audio extracted and formatted for ASR successfully!")
        return output_audio

    except FileNotFoundError:
        print("Error: ffmpeg not found. Please ensure it is installed and added to your PATH.")
        return None
    except Exception as e:
        print("Error extracting audio:", e)
        return None


if __name__ == "__main__":

    video_file = "sample_video.mp4"

    audio = extract_audio(video_file)

    print("Generated audio file:", audio)
