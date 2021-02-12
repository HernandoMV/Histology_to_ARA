#!/usr/bin/python
# # modified from initial code from Constantin Pape: https://github.com/constantinpape/

import sys
import numpy as np
from functions.general_functions import transform_coordinate
from functions.general_functions import parameters_to_matrix
from functions.general_functions import read_mobie_text_output
import os


def register_2D_to_3D_affine(x_coordinates, y_coordinates, res, textfile):
    '''
    Usage: register_2D_to_3D_affine x_coordinate y_coordinate resolution mobie_position.txt
    param x_coordinates: x coordinates (in pixels) of the image
    param y_coordinates: y coordinates (in pixels) of the image
    param resolution: resolution in um/px of the ARA (e.g. 25)
    param mobie_position.txt: path to the output of the MoBIE position

    returns 3D_coord: list of tuples; x, y, z coordinates (in pixels), for the ARA Xum/px
    '''

    # check that all the inputs are correct
    assert isinstance(x_coordinates, list), 'please pass a list for the x coordinates'
    assert isinstance(y_coordinates, list), 'please pass a list for the y coordinates'
    n_points = len(x_coordinates)
    assert n_points == len(y_coordinates), 'lists of different length'
    # check that elastix has been run
    if os.path.isfile(textfile) is False:
        print("I don't find the text file")
        return None

    # initialize list to return
    transformed_points_list = []

    # get the view from bdv
    bdv_view = read_mobie_text_output(textfile)

    # transform to matrix form and pad
    trafo = parameters_to_matrix(bdv_view)

    # calculate the inverse the matrix
    trafo = np.linalg.inv(trafo)

    # points need to be in pixel coordinates
    for i in range(n_points):
        x_coordinate = x_coordinates[i]
        y_coordinate = y_coordinates[i]
        # append a 0 at the end
        pos0 = [int(x_coordinate), int(y_coordinate), 0]

        # transform
        reg0 = transform_coordinate(pos0, trafo)

        # convert from micrometers to pixels
        resolution = int(res)
        pixel_adjusted = [x / resolution for x in reg0]
        transformed_points_list.append(tuple(pixel_adjusted))

    return transformed_points_list


if __name__ == '__main__':
    # check input
    if len(sys.argv) != 5:
        sys.exit('Arguments missing, please run like this:\
            python register_2D_to_3D x_coordinates y_coordinates resolution mobie_position.txt')
    # catch input
    x = sys.argv[1]
    x = list(x.split(','))
    y = sys.argv[2]
    y = list(y.split(','))
    resolution = sys.argv[3]
    textfile = sys.argv[4]
    # run function
    reg_points = register_2D_to_3D_affine(x, y, resolution, textfile)
    print(reg_points)
