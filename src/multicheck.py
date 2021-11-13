import cv2
import csv
from multiviewer_beta import display_images_status, get_annotation_filename, parse_framename
import numpy as np
import pyexcel as pe
import os
import sys


def read_time_points(annotation_files_left, annotation_files_right):
    all_times = []

    for annotation_files in zip(annotation_files_left, annotation_files_right):
        # get tha annotations time points
        time_points = _read_time_points(annotation_files[0],prefix='L') + _read_time_points(annotation_files[1],prefix='R')
        # sort according to the second.
        time_points.sort(key=lambda tup: tup[1])
        all_times.append(time_points)
    time_points_ready = []
    N = len(annotation_files_right)
    M = min([len(T) for T in all_times])
    for j in range(1, M):
        names = [all_times[i][j][0] for i in range(0, N)]
        indices = [all_times[i][j][1] for i in range(0, N)]
        time_points_ready.append([names, indices])
    return time_points_ready


def _filter_sequences(sequences):
    filt_sequences = []
    for i, transition in enumerate(sequences):
        if i + 1 < len(sequences):
            if not transition[2] == sequences[i + 1][2]:
                filt_sequences.append((transition[0], transition[1]))
        else:
            filt_sequences.append((transition[0], transition[1]))
    return filt_sequences


def _read_time_points(annotation_file, prefix=''):
    sequences = []
    with open(annotation_file, 'rb') as csvfile:
        annotations = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in annotations:
            sequences.append((prefix + row[0] + row[1], int(row[1]), row[0]))
    # filtering the transitions
    return _filter_sequences(sequences)

def read_time_points_ods(annotation_file, subsequence, names):
    all_times = []
    for angle in names:
        time_points = _read_time_points_ods(annotation_file,subsequence, angle, 'left_foot') + \
                      _read_time_points_ods(annotation_file,subsequence, angle, 'right_foot')
        # sort according to the second.
        time_points.sort(key=lambda tup: tup[1])
        all_times.append(time_points)
    time_points_ready = []

    N = len(names) # TODO: this is not precise
    lengths = [len(times) for times in all_times]
    # test of equal number of transitions
    if not all(lengths[0] == item for item in lengths):
        print('WARNING: annotations don\'t contain the same number of transtions')
        raw_input("Press Enter to continue...")
    M = min(lengths)
    for j in range(1, M):
        names = [all_times[i][j][0] for i in range(0, N)]
        indices = [all_times[i][j][1] for i in range(0, N)]
        time_points_ready.append([names, indices])
    return time_points_ready

def _read_time_points_ods(annotation_file,subsequence,angle, foot,filter=True):
    sheet_name = subsequence + "-" + '{:03d}'.format(int(angle))
    try:
        data = pe.get_dict(file_name=annotation_file, sheets=[sheet_name])
    except IOError as e:
        print('ERROR: the file: \'' + annotation_file + '\' caused an IO error. Might not be found or corrupted.')
        print(e.message)
        sys.exit(0)
    foot_data = data[foot]
    sequences = []
    if foot.startswith('left'):
        prefix = 'L'
    else:
        prefix = 'R'

    for i, annotation in enumerate(foot_data):
        if annotation == 'NOT_IN_FRAME':
            status = 'n'
        elif annotation == 'IN_THE_AIR':
            status = 'a'
        elif annotation == 'ON_GROUND':
            status = 'g'
        index = i
        sequences.append((prefix + status + str(index), index, status))

    if filter:
        # filtering the transitions
        filtered_sequences = _filter_sequences(sequences)
        filtered_sequences.append((sequences[-1][0],sequences[-1][1]))
    else:
        # just send the converted sequences
        filtered_sequences = sequences

    return filtered_sequences

def get_annotation_file_ods(annotations_path, frame_path):
    sequence_number, sequence_type, person = parse_framename(frame_path)
    subsequence = sequence_type + "-" + sequence_number
    annotation_file_ods = os.path.join(annotations_path,person+'-'+subsequence+'-semiautomatic.ods')
    return annotation_file_ods, subsequence

def check_double_air_ods(annotation_file, subsequence, names):
    for angle in names:
        left_data  = _read_time_points_ods(annotation_file,subsequence, angle, 'left_foot', filter=False)
        right_data =  _read_time_points_ods(annotation_file,subsequence, angle, 'right_foot', filter=False)
        double_air = False
        for item in zip(left_data,right_data):
            if item[0][2] == 'a' and item[1][2]=='a':
                double_air = True
    return double_air



def check(frames1, frames2, frames3, frames4, frames5, name_1='18', name_2='54', name_3='90', name_4='126',
          name_5='162', annotations_path=None, speed=500, autopos=None, ods_mode = False):
    '''
    :param autopos:
    :param frames1: abspath to frames1 files
    :param frames2: and so on
    :param frames3:
    :param frames4:
    :param frames5:
    :param name_1: name of frames1 files
    :param name_2: and so on
    :param name_3:
    :param name_4:
    :param name_5:
    :param offset_path: abs path to where to save the offsets. no further path construction
    :param annotations_path: abs path to where to save the annotations. no further path construction
    :return:
    '''
    # initialization:
    save_offset_flag = False
    save_csv_flag = False

    frames = [frames1, frames2, frames3, frames4, frames5]
    frames = list(map(lambda x: sorted(x, reverse=False), frames))
    names = [name_1, name_2, name_3, name_4, name_5]

    frame_path = frames[0][0]


    i = 0
    animation_index = 0


    if ods_mode:
        [annotation_file_ods, subsequence] = get_annotation_file_ods(annotations_path, frame_path)
        print("checking double air in the ods final annotations...")
        double_air = check_double_air_ods(annotation_file_ods, subsequence, names)
        if double_air:
            raise ValueError('The verification showed that there exist double air annotations.')
        else:
            print('done. OK')
        print("Finding the times points in the ods file...")
        time_points = read_time_points_ods(annotation_file_ods, subsequence, names)
        print('done')

    while 1:
        #compute time points
        if not ods_mode:
            annotation_files_right = list(
                map(lambda x: get_annotation_filename(x, annotations_path, frame_path, 'right'), names))
            annotation_files_left = list(
                map(lambda x: get_annotation_filename(x, annotations_path, frame_path, 'left'), names))
            time_points = read_time_points(annotation_files_left, annotation_files_right)

        # animation counter
        animation_index = animation_index + 1
        if animation_index > 2:
            animation_index = -1
        time_point = time_points[i]
        indices = np.array(time_point[1])

        print("====================")
        print (time_point[0])

        # reading the images:
        selected_indices = animation_index + indices
        try:
            images = list(cv2.imread(f[selected_indices[j]]) for j, f in enumerate(frames))
        except (IndexError):
            print("trying to read images out of the range!!! ")

        # show images and sequence status:
        display_images_status(names, selected_indices, images, frames, autopos)

        # reading the user command
        command_key = cv2.waitKey(speed) & 0xFF
        print(command_key)
        # command acctions

        # decrement
        if command_key in [81, 214, 97] and i - 1 >= 0:
            i = i - 1
            animation_index = -1


        # increment
        if command_key in [83, 196, 100] and i + 1 < len(time_points):
            i = i + 1
            animation_index = -1

        if command_key == 27:
            break
    cv2.destroyAllWindows()

