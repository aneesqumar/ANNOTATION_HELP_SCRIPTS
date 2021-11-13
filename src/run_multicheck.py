import os
import argparse
import time
from utils import get_images_list, correct_path
from multicheck import check

def main():
    parser = argparse.ArgumentParser(description='Tool to verify the sequences transitions from annotation .csv.')
    parser.add_argument('--p-num', metavar='person number', help='person code. Example 001',default='001')
    parser.add_argument('--subsequence', metavar='offset-path', help='sub sequence. Example bg-01',default='bg-01')
    parser.add_argument('--images-path', metavar='path to the images', help='path for the frame images. For example ./example_casia_dir')
    parser.add_argument('--annotations-path', metavar='path to annotations ods/csv', help='path where the annotations are saved')
    parser.add_argument('--image-format', metavar='format', help='format of the images files', default='.jpg')
    parser.add_argument('--speed', metavar='speed', help='time between frames. Default 500ms', default=500, type=int)
    parser.add_argument('--mode', metavar='operation mode', help='mode ods means read the ods file, csv '
                                                             'mode means read the csv file', default='ods', type=str)

    args = parser.parse_args()
    # TODO: change the printing message
    print('==========================================')
    print('=======  Multi Checker v0.1 =========')
    print('==========================================')
    print('    CONTROL KEYS: ')
    print('')
    print('    left cursor : reduce frame count')
    print('    right cursor: increment frame count')
    print('     w: select all angles')
    print('     1: select 18 degrees')
    print('     2: select 54 degrees')
    print('     3: select 90 degrees')
    print('     4: select 126 degrees')
    print('     5: select 162 degrees')
    print('==========================================')
    print('==========================================')
    print('==========================================')

    # inputs that must be given by the user
    p_num = args.p_num
    sub_sequence = args.subsequence

    # hard coded angles
    sequences = ['018', '054', '090', '126', '162']
    win_size = None

    # optional inputs with default values
    image_format = args.image_format # format image
    speed = args.speed # time in miliseconds
    mode = args.mode

    #################################################
    ##      EDIT HERE FOR SIMPLICITY               #
    #################################################

    if not args.images_path:
        # here =>
        images_path_input = "~/gait_project/CASIAData/images/CASIA/DatasetB"
    else:
        images_path_input = args.images_path

    if not args.annotations_path:
        # or here=>
        if mode == 'csv':
            # for csv annotations
            ods_mode = False
            annotations_path_input = \
                "~/gait_project/CASIAData/annotations/CASIA/DatasetB/90degree_annotations"
        elif mode == 'ods':
            # for ods annotations
            ods_mode = True
            annotations_path_input = \
                "~/gait_project/CASIAData/annotations//CASIA/DatasetB/final_annotations"
        else:
            raise ValueError("Argument 'mode' is not correct. Valid values are 'csv' or 'ods' ")
    else:
        ods_mode = mode == 'ods'
        annotations_path_input = args.annotations_path

    # # UNCOMMENT TO TURN ON AUTO POSITIONING
    # # (win_size_x = 360, win_size_y = 430)
    # win_size = (480,320)


    #################################################
    path = correct_path(os.path.join(images_path_input,p_num,sub_sequence))
    annotations_path = correct_path(os.path.join(annotations_path_input,p_num,sub_sequence))

    frames1 = get_images_list(os.path.join(path, sub_sequence + "-" +  sequences[0]), image_format)
    frames2 = get_images_list(os.path.join(path, sub_sequence + "-" +  sequences[1]), image_format)
    frames3 = get_images_list(os.path.join(path, sub_sequence + "-" +  sequences[2]), image_format)
    frames4 = get_images_list(os.path.join(path, sub_sequence + "-" +  sequences[3]), image_format)
    frames5 = get_images_list(os.path.join(path, sub_sequence + "-" +  sequences[4]), image_format)

    start = time.time()
    check(frames1, frames2, frames3, frames4, frames5,
          annotations_path=annotations_path, speed=speed, autopos=win_size, ods_mode=ods_mode)
    print("==========>>> YOUR session lasted....:")
    end = time.time()
    session_time = (end - start)/60
    print(" ------>     {:.2f} minutes".format(session_time))
    print("=======================================")


if __name__ == "__main__":
    # execute only if run as a script
    main()
