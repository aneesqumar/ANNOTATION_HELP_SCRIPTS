import multiviewer_beta as mvbeta
import os
import cv2
from utils import write_json

### json functions
def create_inout_json(filename, names, in_sequences, out_sequences):
    '''
    Create a json file with the inout sequences e.g. [[1,2],[1,2],[1,2],[1,2],[1,2],[1,2]]
    {   in0: 1, in1: 1, in2: 1, in3: 1, in4: 1,, in5: 1,
        out0: 2, out1: 2, out2: 2, out3: 2, out4: 2, out5: 2
    }
    :param filename:
    :param names:
    :param in_sequences, out_sequences:
    :return:
    '''
    print('creating in out json file:')
    value_tuples = []
    # create in tuples
    for i, name in enumerate(names):
        # value_tuples.append(('in' + names[i], inout_sequences[i][0]))
        value_in = None if len(in_sequences[i])==0 else in_sequences[i]
        value_out = None if len(out_sequences[i])==0 else out_sequences[i]
        value_tuples.append(('in' + names[i], value_in))
        value_tuples.append(('out' + names[i], value_out))
    # save in json file
    data = dict(value_tuples)
    write_json(data, filename)


def get_inout_json_filename(offset_path, frames):
    frame_path = frames[0][0]
    sequence_number, sequence_type, person = mvbeta.parse_framename(frame_path)
    json_filename = person + '-' + sequence_type + '-' + sequence_number + '-inout.json'
    return os.path.join(offset_path, json_filename)

### key command functions

def inout_command_action(indices, seqs, target, id):


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
                seqs[5].pop()
            elif target == "all":
                seqs[0].pop()
                seqs[1].pop()
                seqs[2].pop()
                seqs[3].pop()
                seqs[4].pop()
                seqs[5].pop()
        except:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Ups.. error while deleting entrance in your step sequences. Be sure you are not trying to remove "
                  "from an empty array")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    else:
        if 1 <= target <= 6:
            i = target - 1
            seqs[i].append(indices[i])
        elif target == "all":
            for i, seq in enumerate(seqs):
                seq.append(indices[i])
                seqs[i] = seq
    return seqs

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
                seqs[5].pop()
            elif target == "all":
                seqs[0].pop()
                seqs[1].pop()
                seqs[2].pop()
                seqs[3].pop()
                seqs[4].pop()
                seqs[5].pop()
        except:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Ups.. error while deleting entrance in your step sequences. Be sure you are not trying to remove "
                  "from an empty array")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    else:
        if 1 <= target <= 6:
            i = target - 1
            seqs[i].append(id + ',' + str(indices[i]))
        elif target == "all":
            for i, seq in enumerate(seqs):
                seq.append(id + ',' + str(indices[i]))
                seqs[i] = seq
    return seqs


def json_command_action(in_sequences, out_sequences, frames, names, inout_path):
    # if file exist the drop file, overwrite, cancel json-command
    inout_json_filename = get_inout_json_filename(inout_path, frames)
    if os.path.isfile(inout_json_filename):
        print('======================================')
        print('A previous inout json file has beed detected. Select one of this three')
        print('   1. Clear all of them and exit without saving.')
        print('   2. Overwrite them.')
        print('   3. Cancel and continue')
        json_command_key = cv2.waitKey(0) & 0xFF
        if json_command_key == ord('1'):
            mvbeta.delete_json(inout_json_filename)
        elif json_command_key == ord('2'):
            create_inout_json(inout_json_filename, names, in_sequences, out_sequences)
        print('======================================')

    else:
    	#create_inout_json(inout_json_filename, names, inout_sequences)
        create_inout_json(inout_json_filename, names, in_sequences, out_sequences)
    return inout_json_filename
def display_frames(frames1, frames2, frames3, frames4, frames5, frames6,
                   name_1='000', name_2='001', name_3='002', name_4='003', name_5='004', name_6='005',
                   inout_path=None, annotations_path=None, win_size_x=None, win_size_y=None):
    '''
    :param frames1: abspath to frames1 files
    :param frames2: and so on
    :param frames3:
    :param frames4:
    :param frames5:
    :param frames6:
    :param name_1: name of frames1 files
    :param name_2: and so on
    :param name_3:
    :param name_4:
    :param name_5:
    :param name_6:
    :param inout_path: abs path to where to save the offsets. no further path construction
    :param annotations_path: abs path to where to save the annotations. no further path construction
    :return:
    '''
    # initialization:
    if not annotations_path:
        raise NameError("Annotation Path is not defined")
    if not inout_path:
        raise NameError("Offset Path is not defined")

    save_offset_flag = False
    save_csv_flag = False

    frames = [frames1, frames2, frames3, frames4, frames5, frames6]
    frames = list(map(lambda x: sorted(x, reverse=False), frames))
    names = [name_1, name_2, name_3, name_4, name_5, name_6]

    i = 0

    indices = mvbeta.initialize_indices(frames, names, inout_path)

    left_sequences = [[], [], [], [], [], []]
    right_sequences = [[], [], [], [], [], []]
    in_sequences = [[], [], [], [], [], []]
    out_sequences = [[], [], [], [], [], []]
    # TODO: dev/feat_support_6_images: change target behavior
    target = "all"  # four target all three images.
    leg_target = 'left'
    while 1:
        i = i + 1
        # print('iteration ',i)
        # print('frame read: ', frames90[idx_90])
        print('==========================================')
        print('    CONTROL KEYS: ')
        print('')
        # print('    ')
        print('    ESC: exits')
        print('     j/c: save offset file / save annotation file')
        print('     w: select all angles')
        print('     1, 2, 3, 4, 5, 6: select individual angles')
        print('     i/y: insert/delete IN annotation')
        print('     o/u: insert/delete OUT annotation')
        print('     z: reset and realing indices')
        print('==========================================')

        print('target : ', target)
        print('leg target : ', leg_target)
        mvbeta.display_sequences_status(names, right_sequences, 'RIGHT')
        mvbeta.display_sequences_status(names, left_sequences, 'LEFT')
        mvbeta.display_sequences_status(names, in_sequences, 'IN')
        mvbeta.display_sequences_status(names, out_sequences, 'OUT')

        # reading the images:
        images = list(cv2.imread(f[indices[i]]) for i, f in enumerate(frames))

        # show images and sequence status:
        win_size = None
        if win_size_x and win_size_y:
            win_size = (win_size_x, win_size_y)
        mvbeta.display_images_status(names, indices, images, frames, win_size)

        # reading the user command
        command_key = cv2.waitKey(0) & 0xFF
        # os.system('clear')  # works only on linux & macos

        # command acctions

        # decrement
        if command_key in [81, 214] and 1 <= target <= 6:
            i = target - 1
            indices[i] = indices[i] - 1 if indices[i] - 1 >= 0 else 0
        elif command_key in [81, 214] and target == "all" and (indices[3] - 1 >= 0):
            indices = list(map(lambda idx: idx - 1 if idx - 1 >= 0 else 0, indices))

        # increment
        if command_key in [83, 196] and 1 <= target <= 6:
            i = target - 1
            indices[i] = indices[i] + 1 if indices[i] + 1 < len(frames[i]) else len(frames[i]) - 1
        elif command_key in [83, 196] and target == "all" and indices[3] + 1 < len(frames[2]):
            indices = list(map(mvbeta.star(lambda i, idx: idx + 1 if idx + 1 < len(frames[i]) else len(frames[i]) - 1),
                               enumerate(indices)))

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
        if command_key == ord('6'):
            target = 6

        # change leg target
        if command_key == ord('r'):
            leg_target = 'right'
        if command_key == ord('l'):
            leg_target = 'left'

        # command to select all the views
        if command_key == ord('w'):
            target = "all"

        # command to append value to inout_sequences 'in'
        if command_key == ord('i'):
            inout_command_action(indices, in_sequences, target, 'i')

        # command to append value to inout_sequences 'out'
        if command_key == ord('o'):
            inout_command_action(indices, out_sequences, target,'o')

        # command to delete value to inout_sequences 'in'
        if command_key == ord('y'):
            inout_command_action(indices, in_sequences, target, 'd')

        # # command to append value to inout_sequences 'out'
        if command_key == ord('u'):
            inout_command_action(indices, out_sequences, target, 'd')

        # command to add generate json
        if command_key == ord('j'):
            save_offset_flag = True
            json_command_action(in_sequences, out_sequences, frames, names, inout_path)

        # command to reset alignment
        if command_key == ord('z'):
            indices = mvbeta.initialize_indices(frames, names, inout_path)



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
            csv_path = annotations_path

            for i, name in enumerate(names):
                right_csv = mvbeta.get_annotation_filename(name, csv_path, frames[0][0], 'right')
                left_csv = mvbeta.get_annotation_filename(name, csv_path, frames[0][0], 'left')
                mvbeta.save_in_csv(right_csv, right_sequences[i])
                mvbeta.save_in_csv(left_csv, left_sequences[i])
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
        os.system('clear')  # works only on linux & macos
    cv2.destroyAllWindows()
