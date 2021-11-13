import os
import utils
import shutil


# Default directory where to get the images downloaded
AVAMVG_A = "/media/ari/F802A14F02A11422/GAIT_PROJECT/AVAMVG/A"


def parse_folder_name(folder_name):
    '''
    parse the folder structure of a given sequence into the elements of the official folder structure
    :param folder_name: expected input is ..../A/tr01_cam00/
    :return:
    '''
    a = folder_name.split(os.sep)
    person = a[-2]
    tracecam = a[-1]
    subsequence = tracecam[0:2] + "-" + tracecam[2:4]
    cam_number = "0" + tracecam[-2:]
    return person, subsequence, cam_number


def cast_filename(person, subsequence, cam_number, frame):
    '''
    define the name of the file name in the migration directory
    :param person:
    :param subsequence:
    :param cam_number:
    :param frame:
    :return:
    '''
    return person + "-" + subsequence + "-" + cam_number + "_frame_" + frame


def migrate(source_path, dest_path="~/AVAMVG/DatasetB/", copy_mode=True):
    '''
    migrate the images located in the folder source (where you down loaded the data)
    to the dest folder (where you want to place the )
    :param source_path: expected path containing the persons A, B, C...etc
    :param dest_path: output path where the person folders are created
    :param copy_mode: default true. if false will delete the source file after copying it into
    the destination forlder (use to save memory)
    :return:
    '''
    dest_path = utils.correct_path(dest_path)
    for root, dirs, files in os.walk(source_path, topdown=False):
        print("processing" + root)
        for name in files:
            person, subseq, cam_num = parse_folder_name(root)
            name_casted = cast_filename(person, subseq, cam_num, name)
            source_file = os.path.join(root, name)
            dest_file = os.path.join(dest_path, person, subseq, subseq+"-"+cam_num, name_casted)
            utils.mkdirs(dest_file)
            if copy_mode:
                shutil.copy(source_file, dest_file)
            else:
                shutil.move(source_file, dest_file)

