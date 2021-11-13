from subprocess import call
import argparse
import utils
import os
import traceback
import numpy as np
def get_leg_files(side,path):
    '''
    finds all leg files for a side: right or left
    :param side:
    :param path:
    :return:
    '''
    return filter(lambda x: side in x, utils.find_all_files(path,'.csv'))

def get_seqs_by_annotator(annotator_name, status_file_name=utils.DEFAULT_ANNOTATION_STATUS_FILE):
    '''
    :returns the list of p-nums for a given annotator that haven't been dropped
    :param annotator_name:
    :param status_file_name:
    :return:
    '''
    annotators = utils.read_column(status_file_name, 'WHO?')
    # get column p-num
    p_nums = utils.read_column(status_file_name, 'p-num')
    subsequences = utils.read_column(status_file_name, 'subsequence')
    # filter by annotator
    indices = [i for i, x in enumerate(annotators) if x == annotator_name]
    seqs_annotator = [os.path.join('%03d' % int(p_nums[i]),subsequences[i]) for i in indices if p_nums[i] != '']
    # filtering out the people
    seqs_non_dropped = set(get_nondroped_seqs())
    p_nums_final = [seq for seq in seqs_annotator if seq in seqs_non_dropped]
    return p_nums_final

def apply_fix(rules, files, foot, invert=False):
    print(files)
    for f in files:
        frames = utils.read_column(f, 1)
        print('rules')
        print(rules)

        labels = utils.read_column(f, 0)
        print('labels read: ')
        print(labels)

        values = list(map(lambda x: int(x), frames))
        print('values read: ')
        print(values)
        if invert:
            print('inverting....')
            initial_value  = values[0]
            final_value = values[-1]
            i = 0
            for value, label in zip(values, labels):
                # if value is not
                if value - initial_value > 1 and final_value - value > 1:
                    # apply inversion
                    if label == 'g':
                        labels[i] = 'a'
                    elif label == 'a':
                        labels[i] = 'g'
                i += 1

        N = len(labels)
        for i, label in enumerate(labels):
            if i < N-1:
                next_label = labels[i+1]
                # transicion g to a
                cond1 = label == 'g' and next_label == 'a'
                # transition a to g
                cond2 = label == 'a' and  next_label == 'g'
                if cond1:
                    values[i] = values[i]-rules[1]
                elif cond2:
                    values[i] = values[i]-rules[0]

        # move the final values
        values[0] -= rules[0]
        values[-1] -= rules[3]
        # correct overlaps
        for i, label_value  in enumerate(zip(labels,values)):
            if i < len(values)-1:
                current_value = label_value[1]
                next_value = values[i+1]
                if current_value >= next_value:
                    values.pop(i + 1)
                    labels.pop(i + 1)

        print('corrected labels')
        print(labels)
        print('corrected values')
        print(values)
        values = map(lambda x: str(x), values)
        rows = [labels,values]
        print('final result')
        print(rows)
        print('writing leg file: ' + f)
        utils.write_csv(f,rows)


def correct_annotations(manual_annotation_path):
    rules = {'Yiyang':[2,0,1,0], 'Prateek':[1,1,0,3], 'Benjamin':[2,1,1,0]}
    print('Applying corrections....')
    for annotator_name in rules:
        # special case for benjamin
        if annotator_name == 'Benjamin':
            invert = True
        else:
            invert = False
        people = get_seqs_by_annotator(annotator_name)
        if not people:
            print('No data has been found for annotator: ' + annotator_name)
            continue
        print('Corrections for the annotator: ' + annotator_name + '...')
        for person in people:
            # Look in the folder for all the csv and apply rule for the given annotator
            path_to_annotations = os.path.join(manual_annotation_path,person)
            right_files = get_leg_files('right', path_to_annotations)
            apply_fix(rules[annotator_name], right_files, 'right', invert = invert)
            left_files = get_leg_files('left', path_to_annotations)
            apply_fix(rules[annotator_name], left_files, 'left', invert=invert)

def get_nondroped_people(status_file_name=utils.DEFAULT_ANNOTATION_STATUS_FILE):
    notes = utils.read_column(status_file_name, 'Notes')
    p_nums = utils.read_column(status_file_name, 'p-num')
    p_nums = [p_num for p_num, note in zip(p_nums, notes) if not note == 'dropped' and not p_num == '']
    p_nums = ['%03d' % int(p_num) for p_num in p_nums]
    return sorted(list(set(p_nums)))


def get_nondroped_seqs(status_file_name = utils.DEFAULT_ANNOTATION_STATUS_FILE):
    notes = utils.read_column(status_file_name, 'Notes')
    p_nums = utils.read_column(status_file_name, 'p-num')
    subsequences = utils.read_column(status_file_name, 'subsequence')
    p_nums = [os.path.join('%03d' % int(p_num) ,ss) for p_num, note, ss in zip(p_nums, notes, subsequences) if not note == 'dropped' and not p_num == '']
    return sorted(list(set(p_nums)))



def runGeneration(manual_annotation_path,output_path, fixing):

    try:
        if fixing:
            print('=====================================')
            print('=====================================')
            print('     Fixing annotations... ')
            print('=====================================')
            print('=====================================')
            correct_annotations(manual_annotation_path)
        p_nums = get_nondroped_people()
    except AttributeError as e:
        traceback.print_exc()
        print(e)
        print('ERROR: sources/annotationsStatu.csv is not valid')
        return 
    people_path = [os.path.join(manual_annotation_path, s) for s in p_nums]
    print('=====================================')
    print('=====================================')
    print('Executing annotation genererator jar... ')
    print('=====================================')
    print('=====================================')
    for person_path in people_path:
        gen_command = ["java", "-cp", "./sources/annotation-generator-v-3.jar", "com.deeplearning.app.App", "-m",
                   person_path,"-o",output_path]
        call(gen_command)

    print('=====================================')
    print('=====================================')
    print('     FINISH :) ')
    print('=====================================')
    print('=====================================')

def runHelp():
    call(["java", "-cp", "./sources/annotation-generator-v-2.jar",
          "com.deeplearning.app.App", "-h"])


def main():
    parser = argparse.ArgumentParser(description='run the annotation-generation.jar that converts cvs seq into a ods')
    parser.add_argument("annotation_path", metavar='path to annotations csv',
                        help="folder of the csv sequences (example ./90_degree_annotations)")
    parser.add_argument("output_path", metavar='path output annotations ods',
                        help="folder to save the final annotation sheets (example ./final_annotations)")
    parser.add_argument('-f', '--fix', help='flag that activates the fixings', action='store_true')

    args = parser.parse_args()
    manual_annotation_path = str(args.annotation_path)
    ######################
    # Configurations
    #########################
    if not args.fix:
        Fixing = False
    else:
        Fixing = True
    ####################
    output_path = args.output_path
    runGeneration(manual_annotation_path, output_path, fixing = Fixing)


if __name__ == "__main__":
    # execute only if run as a script
    main()
