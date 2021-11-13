import cv2
import os
import argparse
import json
import errno

def star(f):
  return lambda args: f(*args)

def save_in_csv(outfile, step_seq1):
    print('creating csv annotations seq')
    # mkdirs(outfile)
    with open(outfile, 'w') as fp:
        for item in step_seq1:
            fp.write("%s\n" % item)
    print('annotations saved at :' + outfile)


def load_json_offset(json_shift_filename, names):
    with open(json_shift_filename) as f:
        data = json.load(f)
        # +dev: hardcoded to 5 values:
        indices = [0,0,0,0,0]
        central_value = int(data['position' + names[2]])
        indices[2] = central_value
        for i, name in enumerate(names):
            if not i == 2:
                shift = int(data['shift' + names[i]])
                indices[i] = central_value + shift
    return indices

def create_json(filename, indices, names):
    print('creating shifts json file:')
    with open(filename, 'w') as outfile:
        data = dict([('position' + names[2], indices[2])
                        , ('shift' + names[0], indices[0] - indices[2])
                        , ('shift' + names[1], indices[1] - indices[2])
                        , ('shift' + names[3], indices[3] - indices[2])
                        , ('shift' + names[4], indices[4] - indices[2])])
        print(data)
        json.dump(data, outfile)
        print('json created at: ' + filename)


def delete_json(filename):
    print('Deleting the json file name')
    os.remove(filename)


def format_name(name):
    if len(name) < 3:
        name = '0' + name
    return name


def get_json_filename(offset_path, names, frames):
    # +dev: by default the 90 stores the json of shifts.
    if not offset_path:
        middle_frames_file = frames[2][0]
        json_path = os.path.abspath(os.path.join(middle_frames_file, os.pardir))
    else:
        json_path = offset_path
    print("=====> basename")
    print(json_path)
    pos = [p for p, char in enumerate(json_path) if char == '/']
    sequence_number = json_path[pos[-1] + 4: pos[-1]+6]
    sequence_type = json_path[pos[-1] + 1: pos[-1]+3]
    person = json_path[pos[-2] + 1: pos[-1]]
    json_filename = person + '-' + sequence_type + '-' + sequence_number +'-shifts' + names[2] + '.json'
    print("=====> json_filename: ")
    print(json_filename)
    return os.path.join(offset_path, json_filename)


def get_annotation_filename(angle_name, annotations_path, frame_path, leg_id):
    # extrating informationt
    path_list = frame_path.split(os.sep)[:-1]
    sequence_type = path_list[-1]
    sequence_type = sequence_type[:-4]
    fname = '{}-{:03d}-{}.csv'.format(sequence_type, int(angle_name), leg_id)
    return os.path.join(annotations_path, fname)


def json_command_action(indices, frames, names, offset_path):

    #if file exist the drop file, overwrite, cancel json-command
    json_shift_filename = get_json_filename(offset_path, names, frames)
    if os.path.isfile(json_shift_filename):
        print('======================================')
        print('A previous shift json file has beed detected. Do you want to..')
        print('   1. Delete offsets file and NOT save new offsets file.        -(press d)')
        print('   2. overwrite the current offsets file with new offsets file. -(press s)')
        print('   3. Cancel and continue                                       -(press any key)')
        json_command_key = cv2.waitKey(0) & 0xFF
        if json_command_key == ord('d'):
            delete_json(json_shift_filename)
        elif json_command_key == ord('s'):
            create_json(json_shift_filename, indices, names)
        print('======================================')

    else:
        create_json(json_shift_filename, indices, names)
    return json_shift_filename


def annotation_command_action(indices, seqs, target, id):
    if id == 'd':
        try:
            if target == 1:
                seqs[0].pop()
            elif target == 2:
                seqs[1].pop()
            elif target == 3:
                seqs[2].pop()
            elif target == 4:
                seqs[3].pop()
            elif target == 5:
                seqs[4].pop()
            elif target == 6:
                seqs[0].pop()
                seqs[1].pop()
                seqs[2].pop()
                seqs[3].pop()
                seqs[4].pop()
        except:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Ups.. error while deleting entrance in your step sequences. Be sure you are not trying to remove "
                  "from an empty array")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    else:
        if 1 <= target <= 5:
            i = target - 1
            seqs[i].append(id + ',' + str(indices[i]))
        elif target == 6:
            for i, seq in enumerate(seqs):
                seq.append(id + ',' + str(indices[i]))
                seqs[i] = seq
    return seqs

def display_sequences_status(names, sequences, title):
    print('======> ' + title + ' steps annotations status: ')
    for i, name in enumerate(names):
        print('frames' + str(name) + ':' + str(sequences[i]))
    print('=========================================')


def display_images_status(names, indices, images, frames, win_size=None):
    for i, name in enumerate(names):
        print('index ' + name + ' degrees:  ' + str(indices[i]) + '/' + str(len(frames[i]) - 1))
        win_name = 'frames' + name
        cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
        cv2.imshow(win_name, images[i])
        if win_size:
            x, y = win_size # unpack winsize tuple
            win_placements = [(0, y), (0, 0), (x, 0), (2*x, 0), (2*x, y)]
            # placement looks like this
            # 234
            # 1-5
            cv2.resizeWindow(win_name, win_size[0], win_size[1])
            cv2.moveWindow(win_name, *win_placements[i])


def initialize_indices(frames, names, offset_path):
    json_filename = get_json_filename(offset_path,names,frames)
    if os.path.exists(json_filename):
        return load_json_offset(json_filename, names)
    else:
        center_idx = int(len(frames[2]) / 2)
        idx_1 = len(frames[0]) - 1 - center_idx
        idx_2 = len(frames[1]) - 1 - center_idx
        idx_3 = len(frames[2]) - 1 - center_idx
        idx_4 = len(frames[3]) - 1 - center_idx
        idx_5 = len(frames[4]) - 1 - center_idx
        return [idx_1, idx_2, idx_3, idx_4, idx_5]


def display_frames(frames1, frames2, frames3, frames4, frames5,
                   name_1='54', name_2='72', name_3='90', name_4='108', name_5='126',
                   offset_path=None, annotations_path=None, win_size_x=360, win_size_y=430):
    '''
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

    i = 0

    indices = initialize_indices(frames, names, offset_path)

    left_sequences = [[],[],[],[],[]]
    right_sequences = [[],[],[],[],[]]
    target = 6 # four target all three images.
    leg_target = 'left'
    while 1:
        i = i+1
        #print('iteration ',i)
        # print('frame read: ', frames90[idx_90])
        print('==========================================')
        print('    CONTROL KEYS: ')
        print('')
        #print('    ')
        print('    ESC: exits')
        print('     j/c: save offset file / save annotation file')
        print('     w: select all angles')
        print('     1, 2, 3, 4, 5: select individual angles')
        print('==========================================')

        print('target : ', target)
        print('leg target : ', leg_target)
        display_sequences_status(names, right_sequences, 'RIGHT')
        display_sequences_status(names, left_sequences, 'LEFT')

        # reading the images:
        images = list( cv2.imread(f[indices[i]]) for i,f in enumerate(frames))

        # show images and sequence status:
        display_images_status(names, indices, images, frames, (win_size_x, win_size_y))

        # reading the user command
        command_key = cv2.waitKey(0) & 0xFF
        # os.system('clear')  # works only on linux & macos

        # command acctions

        # decrement
        if command_key in [81, 214] and 1 <= target <= 5:
            i = target - 1
            indices[i] = indices[i] - 1 if indices[i] - 1 >= 0 else 0
        elif command_key in [81, 214] and target == 6 and (indices[3]-1>=0):
            indices = list(map(lambda idx: idx - 1 if idx - 1 >= 0 else 0, indices))

        # increment
        if command_key in [83, 196] and 1 <= target <= 5:
            i = target - 1
            indices[i] = indices[i] + 1 if indices[i] + 1 < len(frames[i]) else len(frames[i]) - 1
        elif command_key in [83, 196] and target == 6 and indices[3] + 1 < len(frames[2]):
            indices = list(map(star(lambda i, idx: idx + 1 if idx + 1 < len(frames[i]) else len(frames[i]) - 1), enumerate(indices)))

        # select target with the 1 to 5 keys or all with w key
        if command_key == ord('1'):
            target = 1
        if command_key == ord('2'):
            target = 2
        if command_key == ord('3'):
            target = 3
        if command_key == ord('4'):
            target = 4
        if command_key == ord('5'):
            target = 5
        # change leg target
        if command_key == ord('r'):
            leg_target = 'right'
        if command_key == ord('l'):
            leg_target = 'left'

        # command to select all the views
        if command_key == ord('w'):
            target = 6

        # command to add generate json
        if command_key == ord('j'):
            save_offset_flag = True
            json_command_action(indices, frames, names,offset_path)

        # append to annotation generator
        # case air:
        if command_key == ord('a') and leg_target == 'right':
            right_sequences = annotation_command_action(indices, right_sequences, target, 'a')

        if command_key == ord('a') and leg_target == 'left':
            left_sequences = annotation_command_action(indices, left_sequences, target, 'a')

        # case ground:
        if command_key == ord('g') and leg_target == 'right':
            right_sequences = annotation_command_action(indices, right_sequences, target, 'g')

        if command_key == ord('g') and leg_target == 'left':
            left_sequences = annotation_command_action(indices, left_sequences, target, 'g')

        # append to annotation generator
        if command_key == ord('n') and leg_target == 'right':
            right_sequences = annotation_command_action(indices, right_sequences, target, 'n')

        if command_key == ord('n') and leg_target == 'left':
            left_sequences = annotation_command_action(indices, left_sequences, target, 'n')

        # append to annotation generator
        if command_key == ord('d') and leg_target == 'right':
            right_sequences = annotation_command_action(indices, right_sequences, target, 'd')

        if command_key == ord('d') and leg_target == 'left':
            left_sequences = annotation_command_action(indices, left_sequences, target, 'd')

        if command_key == ord('c'):
            save_csv_flag = True
            print('Saving annotation is the csv files')
            if annotations_path:
                csv_path = annotations_path
            elif offset_path:
                csv_path = offset_path
            else:
                middle_frames_file = frames3[0]
                csv_path = os.path.abspath(os.path.join(middle_frames_file, os.pardir))
            for i, name in enumerate(names):
                right_csv = get_annotation_filename(name, csv_path, frames[0][0], 'right')
                left_csv = get_annotation_filename(name, csv_path, frames[0][0], 'left')
                save_in_csv(right_csv, right_sequences[i])
                save_in_csv(left_csv, left_sequences[i])
            # display_sequences_status(names, right_sequences, 'RIGHT')
            # display_sequences_status(names, left_sequences, 'LEFT')
            import time
            time.sleep(1)

        # if command_key == ord('q'):
        #     cv2.destroyAllWindows()
        #     display_images_status(names, indices, images, frames)

        if command_key == 27:
            if not save_offset_flag or not save_csv_flag:
                print('==========================================')
                if not save_offset_flag and save_csv_flag:
                    print('   ARE YOU SURE YOU WANT TO LEAVE WITHOUT SAVING OFFSET ALIGNMENT? ')
                elif save_offset_flag and not save_csv_flag:
                    print('   ARE YOU SURE YOU WANT TO LEAVE WITHOUT SAVING CSVs ALIGNMENT FILES? ')
                elif not save_offset_flag and not save_csv_flag:
                    print('   ARE YOU SURE YOU WANT TO LEAVE WITHOUT SAVING OFFSETS and CSV ALIGNMENT? ')
                print('     press any key to cancel or ESC to confirm.')
                command_key = cv2.waitKey(0) & 0xFF
                if command_key == 27:
                    break
            else:
                break
        os.system('clear') # works only on linux & macos
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description='Multiviewer to view multiple video clips at once frame by frame')
    parser.add_argument('-frames126', metavar='frames-126', nargs='+', help='target videos to convert at 126')
    parser.add_argument('-frames108', metavar='frames-108', nargs='+', help='target videos to convert at 108')
    parser.add_argument('-frames90', metavar='frames-90', nargs='+', help='target videos to convert at 90')
    parser.add_argument('-frames72', metavar='frames-72', nargs='+', help='target videos to convert at 72')
    parser.add_argument('-frames54', metavar='frames-54', nargs='+', help='target videos to convert at 54')
    parser.add_argument("-v", "--verbosity", nargs=1, help="increase output verbosity")

    args = parser.parse_args()

    verbosity = False
    if args.verbosity:
        verbosity = True
    print('==========================================')
    print('=======  Multi Image Viewer v0.1 =========')
    print('==========================================')
    print('    CONTROL KEYS: ')
    print('')
    print('    left cursor : reduce frame count')
    print('    right cursor: increment frame count')
    print('    ESC: exits')
    print('     j: saves shifts in a json file')
    print('     w: select all angles')
    print('     1: select 54 degrees')
    print('     2: select 72 degrees')
    print('     3: select 90 degrees')
    print('     4: select 108 degrees')
    print('     5: select 126 degrees')
    print('==========================================')
    print('==========================================')
    print('==========================================')
    print('==========================================')
    print('==========================================')

    display_frames(args.frames126, args.frames108, args.frames90, args.frames72, args.frames54)

if __name__ == "__main__":
    # execute only if run as a script
    main()
