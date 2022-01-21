import random
from datetime import datetime
from moviepy.editor import *
from moviepy.config_defaults import *
from numpy import random
from pathlib import Path

import vlog_generator_utils

start_time = datetime.now()

print("Creation Start Time:", start_time.strftime("%H:%M:%S"))
# Record this part yourself daily
# intro_video = VideoFileClip("SourceVideos/2021-07-29.mp4")
source_video_folder_path = Path('SourceVideos')
final_video_folder_path = Path('FinalVideos')
# Put your subtitle file in this folder
annotation_folder_path = Path('SourceSubtitles')
source_music_folder_path = Path('SourceMusic')
source_mixers = Path('Mixers')

annotation_library = (
    vlog_generator_utils.prepare_data_libraries(
        source_video_folder_path,
        final_video_folder_path,
        annotation_folder_path))

# Random cut and load pieces of videos from different places
video_clip_library_filepath = []
video_clip_library_progress = {}
video_clip_library_objects = {}
for file_path in source_mixers.iterdir():
    if file_path.is_file():
        video_clip_library_filepath.append(file_path)

# Add music on top of the existing videos
music_clip_library_filepath = []
music_clip_library_progress = {}
music_clip_library_objects = {}
for file_path in source_music_folder_path.iterdir():
    if file_path.is_file():
        music_clip_library_filepath.append(file_path)

# Load annotations and re-start the video content
# Make the text. Many more options are available.
# txt_clip = ( TextClip("My VLog",fontsize=500,color='white')
#             .set_position(("center", 0.8), relative=True)
#             .set_duration(3) )
for annotation_file_path in annotation_library:
    source_video_file_path = source_video_folder_path / vlog_generator_utils.get_related_video_file_name(
        source_video_folder_path, annotation_file_path)
    intro_video = VideoFileClip(str(source_video_file_path))
    # Use the audio from the video file as the start
    intro_audio = AudioFileClip(str(source_video_file_path))
    # annotation_file = open("2021 07 29 e7edf559b06442b8bdb6e9067a671d61.md", "r")
    annotation_file = open(annotation_file_path, 'r', encoding='utf8')
    annotation_content = annotation_file.readlines()
    # For debugging
    # print(annotation_content)
    # continue
    # annotation_video_clips = [intro_video.subclip(0, 2)]
    annotation_video_clips = [intro_video]
    annotation_music_clips = [intro_audio]
    # annotation_start_time = 2
    annotation_start_time = intro_video.duration
    for line_number in range(len(annotation_content)):
        # load the video clips responsible for producing the final result
        if line_number >= 7:
            annotation_duration = vlog_generator_utils.match_line_content_with_duration(annotation_content[line_number])
            text_to_render = vlog_generator_utils.filter_special_symbols(annotation_content[line_number])
            # do not render empty lines
            if text_to_render.strip() == "":
                continue
            random_number = random.randint(0, len(video_clip_library_filepath))
            if random_number in video_clip_library_progress:
                random_video_file_clip = video_clip_library_objects[random_number]
            else:
                random_video_filepath = video_clip_library_filepath[random_number]
                random_video_file_clip = VideoFileClip(str(random_video_filepath))
                video_clip_library_objects[random_number] = random_video_file_clip

            # load the music clips responsible for producing the final result
            random_number_for_music = random.randint(0, len(music_clip_library_filepath))
            if random_number_for_music in music_clip_library_objects:
                random_music_file_clip = music_clip_library_objects[random_number_for_music]
            else:
                random_music_filepath = music_clip_library_filepath[random_number_for_music]
                random_music_file_clip = AudioFileClip(str(random_music_filepath))
                music_clip_library_objects[random_number] = random_music_file_clip

            # control the progress of the video play
            video_play_starting_point = 0
            if random_number in video_clip_library_progress:
                video_play_starting_point = video_clip_library_progress[random_number]
                # the last part might never show but it's okay
            if video_play_starting_point + annotation_duration > random_video_file_clip.duration:
                video_play_starting_point = 0

            # control the progress of the audio play
            music_play_starting_point = 0
            if random_number_for_music in music_clip_library_progress:
                music_play_starting_point = music_clip_library_progress[random_number_for_music]
            if music_play_starting_point + annotation_duration > random_music_file_clip.duration:
                music_play_starting_point = 0

            # control the video editing and produce the final result
            # sub clip is using the absolute time rather than delta time
            # (t_start, t_end), and not (t_start, duration)
            random_video_to_merge = (random_video_file_clip
                                     .subclip(video_play_starting_point,
                                              video_play_starting_point + annotation_duration)
                                     .set_start(annotation_start_time))
            random_music_to_merge = (random_music_file_clip
                                     .subclip(music_play_starting_point,
                                              music_play_starting_point + annotation_duration)
                                     .set_start(annotation_start_time))

            # control the position to show the text
            # ('centre', 'centre')
            # random.random, range [0, 1)
            position = (random.random(), random.random(), [0.0, 1])
            # random_video_to_merge.fx(vfx.freeze_region, annotation_start_time,
            #                          region=((position[0] * random_video_to_merge.size[0]),
            #                                  (position[1] * random_video_to_merge.size[1]),
            #                                  (position[0] * random_video_to_merge.size[0] + 150),
            #                                  (position[1] * random_video_to_merge.size[1] + 150)))

            annotation_music_clips.append(random_music_to_merge)
            annotation_video_clips.append(random_video_to_merge)
            annotation_video_clips.append(
                vlog_generator_utils.add_text_clips(
                    text_to_render,
                    annotation_start_time,
                    annotation_duration,
                    position))
            video_clip_library_progress[random_number] = video_play_starting_point + annotation_duration
            music_clip_library_progress[random_number_for_music] = music_play_starting_point + annotation_duration
            annotation_start_time += annotation_duration
    annotation_file.close()

    result = CompositeVideoClip(annotation_video_clips)  # Overlay text on video
    resultMusic = CompositeAudioClip(annotation_music_clips)  # Merge all music clips together
    result.audio = resultMusic
    # result.write_videofile("vtest_captioned.mp4", codec='libx264', audio=True, audio_codec='aac')  # Many options...
    result.write_videofile(
        str(final_video_folder_path / vlog_generator_utils.get_related_video_file_name(final_video_folder_path,
                                                                                       annotation_file_path)),
        codec='libx264',
        audio=True,
        audio_codec='aac')
    result.close()

    end_time = datetime.now()
    print('Creation End Time: {0}, Process took {1} in total'.format(
        end_time.strftime("%H:%M:%S"), (end_time - start_time)))
    start_time = end_time
