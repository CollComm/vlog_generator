from moviepy.editor import *
from numpy import interp
from zipfile import ZipFile
from pathlib import Path
import re


def match_line_content_with_duration(content):
    sentence_length = len(content)
    if sentence_length < 5:
        return 1.5
    elif 5 <= sentence_length < 10:
        return 2.5
    elif 10 <= sentence_length < 15:
        return 3.5
    elif 15 <= sentence_length < 20:
        return 4.5
    elif sentence_length >= 20:
        return 5.5


def filter_special_symbols(content):
    new_content = ''
    pre_letter = ''
    for letter in content:
        if letter == '>':
            continue
        elif letter == '-':
            # keep the formula usage like xxx-yyy
            if pre_letter != '' and pre_letter != ' ':
                new_content += letter
            continue
        elif letter == '#':
            continue
        elif letter == '。':
            # suffix symbol
            continue
        else:
            new_content += letter
        pre_letter = letter
    return new_content


def add_text_clips(text, start, duration, position):
    black_screen_white_font = ['你今天吃的什么？',
                               '你今天怎么锻炼身体的？',
                               '你今天睡眠怎么样？',
                               '你学的最重要的一个观点是什么？',
                               '你学的最有趣的一个细节是什么？',
                               '你觉得最难的一件事情是什么？',
                               '你觉得最愧疚或生气的一件事情是什么？',
                               '你最恐惧的一件事情是什么？',
                               '你最感激的十件事情是什么？',
                               '你今天做了多少次拒绝与否的决策？',
                               '你未来想做什么？']
    # Assume position is in the (x, y, range)
    # remap to a more readable form
    position_x = interp(position[0], position[2], [0.2, 0.3])
    position_y = interp(position[1], position[2], [0.2, 0.8])
    adjusted_position = (position_x, position_y)
    # remove extra spacing from the text
    text = str(text).strip()
    if text not in black_screen_white_font:
        if len(text) > 10:
            # insert one line break， ImageMagicK method label necessary
            text = text[:10] + '\n' + text[10:]
        txt_clip = (TextClip(text,
                             font='Alibaba-PuHuiTi-2-55-Regular',
                             fontsize=125,  # 100 is too small for people
                             color='white')  # print_cmd=True is useful for debugging
                    .set_position(adjusted_position, relative=True)
                    .set_duration(duration)
                    .set_start(start))
    else:
        txt_clip = (TextClip(text,
                             font='Alibaba-PuHuiTi-2-55-Regular',
                             fontsize=200,
                             color='white')
                    .set_position(("center", "center"), relative=True)
                    .set_duration(duration)
                    .set_start(start))
    return txt_clip


def prepare_data_libraries(source_video_folder_path,
                           final_video_folder_path,
                           annotation_folder_path):
    assert isinstance(source_video_folder_path, Path)
    assert isinstance(final_video_folder_path, Path)
    assert isinstance(annotation_folder_path, Path)

    intro_video_library = []
    for file_path in source_video_folder_path.iterdir():
        intro_video_library.append(file_path.name)

    final_video_library = []
    for file_path in final_video_folder_path.iterdir():
        final_video_library.append(file_path.name)

    # We only process videos with subtitles
    # We no longer process existing videos
    annotation_library = []
    annotation_xplat_path = Path(annotation_folder_path)
    unzip_annotation_file(annotation_xplat_path / 'zip', annotation_xplat_path / 'MD')
    for file_path in (annotation_xplat_path / 'MD').iterdir():
        if file_path.is_file():
            related_source_video_file_name = get_related_video_file_name(source_video_folder_path, file_path)
            related_final_video_file_name = get_related_video_file_name(final_video_folder_path, file_path)
            if ((related_source_video_file_name in intro_video_library)
                    and (related_final_video_file_name not in final_video_library)):
                annotation_library.append(file_path)

    return annotation_library


def unzip_annotation_file(annotation_folder_zip_path, annotation_folder_md_path):
    """
    We support zipped file that are stored in zip format.
    """
    for file_path in annotation_folder_zip_path.iterdir():
        if not file_path.stem:
            continue
        if file_path.suffix == '.zip':
            with ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(annotation_folder_md_path)


def get_related_video_file_name(source_video_folder_path, annotation_file_path):
    """
      we expect the annotation to be in SourceSubtitles/2021 07 29 XYZ.md
      or in the form of 2021 07 29 XYZ.md
    """
    pattern = re.compile(r'.*?(\d+) (\d+) (\d+) .*')
    match = pattern.match(annotation_file_path.name)
    if not match:
        raise (Exception(
            'Annotation file {} with {} is in the wrong format.'.format(
                annotation_file_path, source_video_folder_path)))
    video_file_path = source_video_folder_path / '{}-{}-{}.mp4'.format(match.group(1), match.group(2), match.group(3))
    return video_file_path.name
