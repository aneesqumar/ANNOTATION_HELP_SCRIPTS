import click
from avamvg_migration import migrate


epilog = '''
    a wrapper to run the folder migration from original to official structure
'''


@click.command()
@click.help_option(help="Run the migration of the downloaded AVAMVG dataset into the official folder structure.")
@click.option('--avamvg-dir',
              #################################
              # EDIT SOURCE FILE HERE
              #################################
              default=r'/media/ron/3c2f7824-fbf5-4427-9f1a-fbbc8292f364/rabinf24.uco.es/avamvg/dataset/imgs/',
              #################################
              help="path to original dataset directory")
@click.option('--dest-dir',
              #################################
              # EDIT DESTINATION FOLDER HERE
              #################################
              default="/media/ron/3c2f7824-fbf5-4427-9f1a-fbbc8292f364/AVAMVG/",
              #################################

              help="path to the destination directory")
def main(avamvg_dir, dest_dir):
    kwargs = {'source_path': avamvg_dir, 'dest_path': dest_dir}


    migrate(**kwargs)

if __name__ == "__main__":
    main()
