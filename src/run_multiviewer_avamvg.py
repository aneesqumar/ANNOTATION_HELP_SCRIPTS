import click
from multiviewer6 import display_frames
import glob
import os
import utils
angles = [0,1,2,3,4,5]

epilog = '''
    a wrapper to make multiviewer avamvg easier to use

'''


@click.command()
@click.help_option(help="a wrapper to make the multiviewer easier to use.")

@click.option('--images-dir',
              default=r'/media/ron/3c2f7824-fbf5-4427-9f1a-fbbc8292f364/AVAMVG/openpose',
              help="root directory to images")

@click.option('--p-num', default="A", help="subpath to person case")
@click.option('--subsequence', default="tr-01", help="subpath to subsequence")
@click.option('--extension', default=".png", help="extension of frame files")
@click.option('--offset-root',
              default=r'/home/ron/Dokumente/Datasets/Gait/Repositories/Gait_Annotations/Gait_anotations/AVAMVG/not_in_frame_annotations/',
              help="where to save offsets")
@click.option('--annotations-root',
              default=r'/home/ron/Dokumente/Datasets/Gait/Repositories/Gait_Annotations/Gait_anotations/AVAMVG/semiautomatic_annotations/',
              help="where to save annotations")

def main(images_dir, p_num, subsequence, extension, offset_root, annotations_root):
    images_dir = utils.correct_path(images_dir)

    annotations_root = utils.correct_path(annotations_root)
    offset_root = utils.correct_path(offset_root)

    extension = ".png"

    front_path = os.path.join(images_dir, p_num, subsequence)

    frame_folders = [os.path.join(front_path, "{}-{:03d}".format(subsequence, a)) for a in angles]
    frame_folders = [os.path.join(f, '*{}'.format(extension)) for f in frame_folders]

    frame_files = list(map(lambda x: glob.glob(os.path.abspath(x)), frame_folders))


    kwargs = {
        'frames{}'.format(i+1) : f for i,f in enumerate(frame_files)
    }
    kwargs.update(
        {
            "name_{}".format(i+1) : str(a) for i, a in enumerate(angles)
        }
    )
    kwargs.update(
        {"inout_path": os.path.join(offset_root, '{}'.format(p_num), subsequence),
         "annotations_path": os.path.join(annotations_root, '{}'.format(p_num), subsequence)}
    )

    ## UNCOMMENT TO TURN ON AUTO POSITIONING
    # kwargs.update(
    #     {"win_size_x": 360,
    #      "win_size_y": 430}
    # )

    display_frames(**kwargs)

if __name__ == "__main__":
    main()
