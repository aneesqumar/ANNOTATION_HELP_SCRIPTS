import click
from multiviewer5 import display_frames
import glob
import os

angles = [18, 54, 90, 126, 162,]

epilog = '''
    a wrapper to make multiviewer 5 easier to use
    angles are hard coded
    angles = [18, 54, 90, 126, 162,]
    Assumed file-structure:
    casia_dir/p_num/subsequence/subsequence-angle/000.jpg
    casia_dir/p_num/subsequence/subsequence-angle/001.jpg
    ...
    
    example:
    ~/CASIA/DatasetB_processed/p001/bg-01/bg-01-000/000.jpg
    ~/CASIA/DatasetB_processed/p001/bg-01/bg-01-000/001.jpg
'''


@click.command()
@click.help_option(help="a wrapper to make the multiviewer easier to use.")
@click.option('--casia-dir',
              default=r'/media/sandro/Volume/Datasets/CASIA/DatasetB_processed/',
              help="root directory to casia B video files")
@click.option('--p-num', default="001", help="subpath to person case")
@click.option('--subsequence', default="bg-01", help="subpath to subsequence")
@click.option('--extension', default=".jpg", help="extension of frame files")
@click.option('--offset-root',
              default=r'/media/sandro/Volume/Datasets/GaitPhaseDataAnnotations/CASIA/DatasetB/offsets/',
              help="where to save offsets")
@click.option('--annotations-root',
              default=r'/media/sandro/Volume/Datasets/GaitPhaseDataAnnotations/CASIA/DatasetB/90degree_annotations/',
              help="where to save annotations")
@click.option('--win-size-x',
              default=360,
              help='window size x')
@click.option('--win-size-y',
              default=460,
              help='window size y')
def main(casia_dir, p_num, subsequence, extension, offset_root, annotations_root, win_size_x, win_size_y):
    front_path = os.path.join(casia_dir, p_num, subsequence)
    frame_folders = [os.path.join(front_path, "{}-{:03d}".format(subsequence, a)) for a in angles]
    frame_folders = [os.path.join(f, '*{}'.format(extension)) for f in frame_folders]

    frame_files = list(map(lambda x: glob.glob(x), frame_folders))

    kwargs = {
        'frames{}'.format(i+1) : f for i,f in enumerate(frame_files)
    }
    kwargs.update(
        {
            "name_{}".format(i+1) : str(a) for i, a in enumerate(angles)
        }
    )
    kwargs.update(
        {"offset_path" : os.path.join(offset_root, '{}'.format(p_num), subsequence),
         "annotations_path" : os.path.join(annotations_root, '{}'.format(p_num), subsequence),
         'win_size_x' : win_size_x,
         'win_size_y' : win_size_y
         }
    )

    display_frames(**kwargs)

if __name__ == "__main__":
    main()