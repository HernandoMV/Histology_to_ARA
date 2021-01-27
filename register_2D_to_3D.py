#!/usr/bin/python
# # modified from initial code from Constantin Pape: https://github.com/constantinpape/

import sys
import numpy as np
from helpers.helpers import transform_coordinate
from helpers.helpers import parameters_to_matrix
from helpers.helpers import read_mobie_text_output


def register_2D_to_3D_affine():
    '''
    Usage: register_2D_to_3D_affine x_coordinate y_coordinate resolution mobie_position.txt
    param x_coordinate: x coordinate (in pixels) of the image
    param y_coordinate: y coordinate (in pixels) of the image
    param resolution: resolution in um/px of the ARA (e.g. 25)
    param mobie_position.txt: path to the output of the MoBIE position

    returns 3D_coord: x, y, z coordinates (in pixels), for the ARA Xum/px
    '''

    # TODO: check that all the inputs are correct
    if len(sys.argv) < 5:
        sys.exit('Arguments missing, please run like this:\
            register_2D_to_3D_affine x_coordinate y_coordinate resolution mobie_position.txt')

    # get the view from bdv
    bdv_view = read_mobie_text_output(sys.argv[4])
    
    # transform to matrix form and pad
    trafo = parameters_to_matrix(bdv_view)
    
    # calculate the inverse the matrix
    trafo = np.linalg.inv(trafo)

    # points need to be in pixel coordinates
    # append a 0 at the end
    pos0 = [int(sys.argv[1]), int(sys.argv[2]), 0]

    # transform
    reg0 = transform_coordinate(pos0, trafo)

    # convert from micrometers to pixels
    resolution = int(sys.argv[3])
    pixel_adjusted = [x / resolution for x in reg0]
    print(pixel_adjusted)
    
    return pixel_adjusted


if __name__ == '__main__':
    register_2D_to_3D_affine()
