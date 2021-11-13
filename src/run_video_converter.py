import video_2_frame_folder as video_converter
import argparse
import os
import fnmatch
from tqdm import tqdm

def get_output_path(video,output_path):
    # expected value is: 001-bg-01-000.avi
    parts = os.path.basename(video).split('.')[0].split('-')
    if len(parts)==4:
        person = parts[0]
        subsequence = parts[1] + "-" + parts[2]
        angle = parts[1] + "-" + parts[2] + "-" + parts[3]
        return os.path.join(output_path, person, subsequence, angle)
    else:
        return None



def find_all_videos(input_path):
    videos = []
    pattern = "*.avi"
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if fnmatch.fnmatch(file, pattern):
                videos.append(os.path.join(root,file))
    # print(videos)
    return videos


def correct_path(path):
    if path.startswith('~'):
        path = os.path.expanduser(path)
    return os.path.abspath(path)


def main():
    parser = argparse.ArgumentParser(description='Video converter simplified')
    parser.add_argument('-p', '--path', metavar='input_path', type=str, help='path where to find the videos (format avi)')
    parser.add_argument('-o', '--output', metavar='output_path', help='path where to save frame images')
    args = parser.parse_args()
    input_path = correct_path(args.path)
    output_path = correct_path(args.output)
    print("finding videos...")
    videos = find_all_videos(input_path)
    print("processing videos...")
    skipped = []
    for video in tqdm(videos):
        frames_output_path = get_output_path(video,output_path)
        if frames_output_path:
            tqdm.write(video)
            video_converter.create_frame_folder(video, output=frames_output_path)
        else:
            skipped.append(video)
    print ("Done")
    print("skipped videos: ")
    for v in skipped:
        print(v)

if __name__ == '__main__':
    main()