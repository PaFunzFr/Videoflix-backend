import subprocess

def convert_video_480p(source):
    target_file = source + '_480p.mp4'
    cmd='ffmpeg-i"{}"-shd720-c:vlibx264-crf23-c:aaac-strict-2"{}"'.format(source, target_file)
    run = subprocess.run(cmd,capture_output=True) # subprocess => start process from terminal