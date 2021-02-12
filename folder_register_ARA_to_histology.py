#!/usr/bin/python
# Hernando M Vergara Feb 2021
# folder_register_ARA_to_histology.py

import sys
import os
import glob
import shutil
from functions.general_functions import get_elastix_paths


def folder_register():

    # check that it is run correctly
    if len(sys.argv) != 2:
        sys.exit('Wrong call, please run like this:\
            python folder_register_ARA_to_histology.py path_to_folder')

    # Specify paths
    elastix_path, _, = get_elastix_paths()
    parameters_path = os.path.abspath(__file__ + "/../registration_parameters/")
    affine_name = '01_ARA_affine.txt'
    bspline_name = '02_ARA_bspline.txt'

    # Get the directory as the first imput parameter
    folder_path = sys.argv[1]
    print('Performing registrations in folder {}'.format(folder_path))

    # Parse the files
    ARA, histology, _ = split_files_in_registration_folder(folder_path)

    # Perform registrations
    for i in range(len(ARA)):
        ara_file = os.path.basename(ARA[i])
        hist_file = os.path.basename(histology[i])
        print('Registering {} to {}'.format(ara_file,
                                            hist_file))

        # Create output directory
        outdir = hist_file.split('.tif')[0] + '_reg_output'
        outdir_path = os.path.join(folder_path, outdir)
        if not os.path.exists(outdir_path):
            os.makedirs(outdir_path)

        # Copy files to the directory and move there for the registration
        os.chdir(outdir_path)
        shutil.copy(os.path.join(parameters_path, affine_name), './')
        shutil.copy(os.path.join(parameters_path, bspline_name), './')
        shutil.copy(histology[i], './')
        shutil.copy(ARA[i], './')

        # Run registration

        regist_command = '{0} -f {1} -m {2} -p {3} -p {4} -out {5}'.format(elastix_path,
                                                                           hist_file,
                                                                           ara_file,
                                                                           affine_name,
                                                                           bspline_name,
                                                                           './')

        os.system(regist_command)

    print('Done')


def split_files_in_registration_folder(path):
    '''
    Splits files of those ending in '[number].tif', '_ARA.tif', and '.txt'
    '''
    ARAlist = glob.glob(os.path.join(path, '*_ARA.tif'))
    histlist = glob.glob(os.path.join(path, '*[0-9].tif'))
    txtlist = glob.glob(os.path.join(path, '*.txt'))

    return (ARAlist, histlist, txtlist)


if __name__ == '__main__':
    folder_register()
