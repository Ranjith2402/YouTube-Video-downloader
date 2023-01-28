import ffmpeg
from kivy.core.audio import SoundLoader


# Input and output file paths
input_file = ffmpeg.input("C:\\Users\\ranji\\Music\\youtube_video_downloader\\Music\\Earl - All That Glitters (Official Video).ogg")
output_file = 'C:\\Users\\ranji\\music\\youtube_video_downloader\\Music\\Earl - All That Glitters (Official Video).mp3'

# SoundLoader().load(output_file).play()

# Run the conversion
# (
#     ffmpeg
#     .input(input_file)
#     .output(output_file, acodec='pcm_s16le', ar='44100', channels=2)
#     .run()
# )

input_file.output(output_file, acodec='pcm_s16e', ar='44100').run()
