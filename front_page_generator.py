import random
from pathlib import Path
import cv2

import front_page_generator_utils

# This folder stores the videos used for producing front page
final_video_folder_path = Path('FinalVideos')

# This folder stores the resulting front page
front_page_folder_path = Path('FrontPages')

# Number of front pages generated per video
num_front_pages = 10

for file_path in final_video_folder_path.iterdir():
    if file_path.is_file():
        print(file_path)
        cap = cv2.VideoCapture(str(file_path))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        current_frame_number = 0
        current_front_page_id = 0
        selected_frames = list(
            map(lambda x: random.randint(0, frame_count - 1),
                list(range(num_front_pages))))
        print(selected_frames)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if current_frame_number in selected_frames:
                result = front_page_generator_utils.smooth_glass_effect(frame)
                result = front_page_generator_utils.add_timestamp(result, file_path)

                front_page_file_path = (front_page_folder_path / file_path.stem)
                front_page_file_path.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(
                    str(front_page_file_path / ('{0}.png'.format(current_front_page_id))),
                    result)
                current_front_page_id += 1
            current_frame_number += 1

print('Processing Done')
