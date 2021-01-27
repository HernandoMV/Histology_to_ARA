import numpy as np

def parameters_to_matrix(trafo):
    # function from https://github.com/constantinpape/elf
    """ Parameter vector to affine matrix.
    Assumes parameter vector layed out as
    2d:
        [a00, a01, a02, a10, a11, a12]
    3d:
        [a00, a01, a02, a03, a10, a11, a12, a13, a20, a21, a22, a23]
    """
    if len(trafo) == 12:
        sub_matrix = np.zeros((3, 3), dtype='float64')
        sub_matrix[0, 0] = trafo[0]
        sub_matrix[0, 1] = trafo[1]
        sub_matrix[0, 2] = trafo[2]

        sub_matrix[1, 0] = trafo[4]
        sub_matrix[1, 1] = trafo[5]
        sub_matrix[1, 2] = trafo[6]

        sub_matrix[2, 0] = trafo[8]
        sub_matrix[2, 1] = trafo[9]
        sub_matrix[2, 2] = trafo[10]

        shift = [trafo[3], trafo[7], trafo[11]]

        matrix = np.zeros((4, 4))
        matrix[:3, :3] = sub_matrix
        matrix[:3, 3] = shift
        matrix[3, 3] = 1

    elif len(trafo) == 6:
        sub_matrix = np.zeros((2, 2), dtype='float64')
        sub_matrix[0, 0] = trafo[0]
        sub_matrix[0, 1] = trafo[1]

        sub_matrix[1, 0] = trafo[3]
        sub_matrix[1, 1] = trafo[4]

        shift = [trafo[2], trafo[5]]

        matrix = np.zeros((3, 3))
        matrix[:2, :2] = sub_matrix
        matrix[:2, 2] = shift
        matrix[2, 2] = 1

    else:
        raise ValueError(f"Invalid number of parameters {len(trafo)}")

    return matrix


def transform_coordinate(coord, matrix):
    # function from https://github.com/constantinpape/elf
    # x = matrix[0, 0] * coord[0] + matrix[0, 1] * coord[1] + matrix[0, 2] * coord[2] + matrix[0, 3]
    # y = matrix[1, 0] * coord[0] + matrix[1, 1] * coord[1] + matrix[1, 2] * coord[2] + matrix[1, 3]
    # z = matrix[2, 0] * coord[0] + matrix[2, 1] * coord[1] + matrix[2, 2] * coord[2] + matrix[2, 3]
    ndim = len(coord)
    return tuple(sum(coord[jj] * matrix[ii, jj] for jj in range(ndim)) + matrix[ii, -1] for ii in range(ndim))


def read_mobie_text_output(filepath):
    # reads the bdv from a .txt file of the MoBIE output
    with open(filepath) as fp:
        for i, line in enumerate(fp):
            if i == 3:
                view = line.strip()
                break
    pview = np.array(view.split(','))
    pview = [float(i) for i in pview]

    return pview