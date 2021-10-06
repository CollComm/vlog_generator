from moviepy.editor import *


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
            if pre_letter != '':
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


def add_text_clips(text, start, duration):
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
    if text.strip() not in black_screen_white_font:
        txt_clip = (TextClip(text,
                             font='Alibaba-PuHuiTi-2-55-Regular',
                             fontsize=150,  # 100 is too small for people
                             color='white')  # print_cmd=True is useful for debugging
                    .set_position(("center", 0.8), relative=True)
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
    intro_video_library = []
    for root, dirs, files in os.walk(source_video_folder_path):
        for file in files:
            intro_video_library.append('{}/{}'.format(source_video_folder_path, file))

    final_video_library = []
    for root, dirs, files in os.walk(final_video_folder_path):
        for file in files:
            final_video_library.append('{}/{}'.format(final_video_folder_path, file))

    # We only process videos with subtitles
    # We no longer process existing videos
    annotation_library = []
    for root, dirs, files in os.walk(annotation_folder_path):
        for file in files:
            related_source_video_file_name = get_related_video_file_name(source_video_folder_path, file)
            related_final_video_file_name = get_related_video_file_name(final_video_folder_path, file)
            if ((related_source_video_file_name in intro_video_library)
                    and (related_final_video_file_name not in final_video_library)):
                annotation_library.append('{}/{}'.format(annotation_folder_path, file))

    return annotation_library


def get_related_video_file_name(source_video_folder_path, annotation_file):
    """
      we expect the annotation to be in SourceSubtitles/2021 07 29 XYZ.md
      or in the form of 2021 07 29 XYZ.md
    """
    if isinstance(annotation_file, str):
        folder_position = annotation_file.find('/')
        if folder_position != -1:
            parts = annotation_file.split('/')[1].split()
        else:
            parts = annotation_file.split()
        if len(parts) < 4:
            raise (Exception(
                'Annotation file {} with {} is in the wrong format.'.format(
                    annotation_file, source_video_folder_path)))
        return '{}/{}-{}-{}.mp4'.format(source_video_folder_path, parts[0], parts[1], parts[2])

