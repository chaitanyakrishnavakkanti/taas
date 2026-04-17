import os


def ensure_ffmpeg_in_path():
    """
    Add a bundled ffmpeg binary to PATH when available.
    """
    try:
        import imageio_ffmpeg
    except Exception:
        return None

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    path_value = os.environ.get("PATH", "")
    if ffmpeg_dir and ffmpeg_dir not in path_value:
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + path_value
    return ffmpeg_exe
