import cv2
import os
import argparse

def get_target_directory(target):
    return target.split('.')[0]

def create_frame_folder(target_file, verbosity=False, change_size=(640,480), output=''):
    if len(output)>0:
        target_directory = output
    else:
        target_directory = get_target_directory(target_file)
    if verbosity:
        print('output for file {} at {}: '.format(target_file.split('/')[-1],target_directory))
    # creating directory
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
    vidcap = cv2.VideoCapture(target_file)
    success,image = vidcap.read()
    # print('>>>>>>>>>> sucess type:',type(success))
    if success and change_size:
        image = cv2.resize(image,change_size)
    count = 0
    success = True
    while success:
        file_name = target_file.split('/')[-1]
        file_name = file_name.split('.')[0]
        frame_file = "%s/%s_frame_%03d.jpg" % (target_directory,file_name,count)
        frame_file = frame_file.replace(' ','\ ')
        success,image = vidcap.read()
        if success and change_size:
            # print("------>>> change_size",change_size)
            # print("----->>>image.shape",image.shape)
            image = cv2.resize(image,change_size)
        if verbosity:
            print('Read a new frame: ', success)
            print('saving frame: ',frame_file)
        if success:
            cv2.imwrite(frame_file, image)     # save frame as JPEG file
            count += 1
# +dev: this has to be injected throuth the command linet
# target_file = '001-bg-02-162.avi'


def main():
    parser = argparse.ArgumentParser(description='Convert avi to folder of jpg frame files.')
    parser.add_argument('videos', metavar='videos-list', nargs='+', help='target videos to convert')
    parser.add_argument('-o', '--output', metavar='outputDir', nargs=1, help='directory to create the jpg frame files')
    parser.add_argument('-z', '--resize', metavar='resize', type=int, nargs=2, help='new size of the output image')
    parser.add_argument("-v", "--verbosity", help="increase output verbosity")
    args = parser.parse_args()
    # print(args)
    verbosity = False
    if args.verbosity:
        verbosity = True
    output = ''
    if args.output:
        output = args.output
    change_size = None
    if args.resize:
        change_size = (args.resize[0], args.resize[1])
    print('processing files...')
    for videos in args.videos:
        if not videos.endswith('.avi'):
            if verbosity:
                print('entry ', videos, ' ignored.')
            continue
        if len(output) > 0:
            create_frame_folder(videos, verbosity, change_size, output)
        else:
            create_frame_folder(videos, verbosity, change_size)
    print('Done without errors')
