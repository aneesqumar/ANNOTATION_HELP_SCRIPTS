import csv
import os
import errno
import json
import copy

DEFAULT_ANNOTATION_STATUS_FILE = 'sources/annotationStatus.csv'


def parse_csv(filename, with_header = True):
    '''
    Parse file names and output a dict of lists
    :param filename:
    :return: dict of columns: {'col name': 'values list'}
    '''
    with open(filename, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='/')
        columns = {}
        if with_header:
            headers = csvreader.next()
            for h in headers:
                columns[h] = []
        else:
            first_row = csvreader.next()
            headers = range(0,len(first_row))
            for h,v in  zip(headers,first_row):
                columns[h] = [v]
        for row in csvreader:
            for h, v in zip(headers, row):
                columns[h].append(v)
    return columns

def read_column(filename, columnname):
    if isinstance(columnname, (int, long)):
        columns = parse_csv(filename, with_header=False)
        return columns[columnname]
    else:
        columns = parse_csv(filename)
        return columns[columnname]


def mkdirs(outfile):
    if not os.path.exists(os.path.dirname(outfile)):
        try:
            os.makedirs(os.path.dirname(outfile))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def correct_path(path):
    '''
    Correct the path when it statrs the with ~ (LINUX MAXOS case)
    :param path:
    :return:
    '''
    if path.startswith('~'):
        path = os.path.expanduser(path)
    return os.path.abspath(path)

def get_images_list(path,image_format):
    '''
    Generates a list of image files in a path with a given format

    :param path: path to the images files
    :param image_format: format od the images exaple .jpg
    :return:
    '''
    result = []
    for image_file in os.listdir(path):
        if image_file.endswith(image_format):
            result.append(os.path.join(path, image_file))
    return result
def write_csv(file, rows):
    if os.path.exists(file):
        os.remove(file)
    with open(file, 'w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for r in zip(*rows):
            csv_writer.writerow(r)

def write_json(data, filename):
    '''
    write data in a json named in the filename (path to file)
    :param data:
    :param filename:
    :return:
    '''
    with open(filename, 'w') as outfile:
        print(data)
        json.dump(data, outfile)
        print('json created at: ' + filename)

def find_all_files(input_path, ending):
    '''
    find all files with endnin
    :param input_path:
    :param ending:
    :return:
    '''
    input_path_co = correct_path(input_path)
    output_files = []
    print('Exploring folder for \'' +  ending + '\' files. In folder ' + input_path_co)
    for root, dirs, files in os.walk(input_path_co):
        for file in files:
            if file.startswith('.'):
                continue
            if file.endswith(ending): #fnmatch.fnmatch(file, ending):
                output_files.append(os.path.join(root,file))
    print(str(len(output_files)) + ' files found.' if len(output_files) else 'No files found.')
    return output_files

def ls_pwd():
    '''
    print all  files in currecnt directy. used for debugging
    :return:
    '''
    path = '.'
    files = os.listdir(path)
    for name in files:
        print(name)