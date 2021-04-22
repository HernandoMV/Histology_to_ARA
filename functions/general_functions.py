#!/usr/bin/python

import numpy as np
import os
import pandas as pd


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


def get_elastix_paths():
    # this is where the file is supposed to be:
    infofile_path = os.path.abspath(__file__ + "/../../custom_paths_to_elastix.txt")
    file = open(infofile_path)
    lines = file.readlines()
    for line in lines:
        if line.startswith('elastix_path = '):
            ep = line.split('elastix_path = ')[1].strip()
        if line.startswith('transformix_path = '):
            tp = line.split('transformix_path = ')[1].strip()
    file.close()

    return(ep, tp)


def make_reg_core_name_from_series(series_data):
    '''
    series_data is a panda series with specific columns
    outputs: PH301_A2A-Ai14_slide-1_slice-0
    '''
    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    name = '_'.join([series_data.AnimalID,
                     series_data.ExperimentalCondition,
                     'slide-' + series_data.Slide,
                     'slice-' + series_data.Slice])
    return name


def make_core_name_from_series(series_data):
    '''
    series_data is a panda series with specific columns
    outputs: PH301_A2A-Ai14_slide-1_slice-0_manualROI-L-Tail
    '''
    # PH301_A2A-Ai14_slide-1_slice-0_manualROI-L-Tail
    assert isinstance(series_data, pd.Series), 'Data not pandas series'
    name = '_'.join([make_reg_core_name_from_series(series_data),
                     'manualROI-' + series_data.Side + '-' + series_data.AP])
    return name


def get_prereg_coordinates(df, data_path):
    '''
    df is a panda dataframe with specific columns
    datapath is the path to the images
    outputs: general coordinates of cell in downsampled image
    '''
    assert isinstance(df, pd.DataFrame), 'Data not pandas dataframe'

    # create two columns to hold data
    df['x_coord_pre'] = np.nan
    df['y_coord_pre'] = np.nan

    # get the individual manual rois
    ind_rois = df.manual_roi_name.unique()
    # iterate over each manually draw roi
    for roiname in ind_rois:
        # get the indexes of the cells belonging to that roi
        sub_idx = df[df.manual_roi_name == roiname].index.values
        # get the path to the file with roi information
        mr_file = get_manual_rois_file_path(df.loc[sub_idx], data_path)
        # generate a dataframe from that file
        roi_df = create_dataframe_from_roi_file(mr_file)

        # iterate over the indexes
        for index, row in df.loc[sub_idx].iterrows():
            # get roi number
            rn = str(row.ROI)
            roi_df_bool = roi_df.roiID == rn
            # get high resolution x and y values
            hr_x = int(roi_df[roi_df_bool].high_res_x_pos) + float(row.Center_X)
            hr_y = int(roi_df[roi_df_bool].high_res_y_pos) + float(row.Center_Y)
            # adjust resolution
            reg_im_res = float(roi_df[roi_df_bool].registration_image_pixel_size)
            coords_res = float(roi_df[roi_df_bool].high_res_pixel_size)
            lr_x = int(hr_x * coords_res / reg_im_res)
            lr_y = int(hr_y * coords_res / reg_im_res)
            # assign to dataframe columns
            df.at[index, 'x_coord_pre'] = lr_x
            df.at[index, 'y_coord_pre'] = lr_y

    return df


def create_dataframe_from_roi_file(filepath):
    '''
    creates a dataframe with information of rois
    '''
    # initialize list to hold the data
    rois_list = []
    # read from the file and populate the dictionary
    linecounter = 0
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            parts = line.split(', ')
            # read column names from first line
            if linecounter == 0:
                columns = parts
            else:  # append to the list
                rois_list.append(parts)
            linecounter += 1

    # create the dataframe
    rois_df = pd.DataFrame(data=rois_list, columns=columns)

    return(rois_df)


def get_manual_rois_file_path(df, data_path):
    '''
    generates the path to the file with the rois information
    '''
    rois_file_path = 'ROIs/000_ManualROIs_info/'
    manual_roi_path = os.path.join(data_path,
                                   df.AnimalID.unique()[0],
                                   rois_file_path,
                                   make_core_name_from_series(df.iloc[0]))
    manual_roi_path = '_'.join([manual_roi_path,
                               'roi_positions.txt'])

    return (manual_roi_path)


def get_transformation_file_path(general_path, image_name):
    '''
    generates the path to the file with the elastix transformation
    '''
    registration_file_path = 'ROIs/000_Slices_for_ARA_registration/'
    out_path = os.path.join(general_path,
                            registration_file_path,
                            image_name + '_reg_output',
                            'TransformParameters.1.txt')

    return out_path


def get_mobie_file_path(general_path, image_name):
    '''
    generates the path to the file with the mobie position
    '''
    registration_file_path = 'ROIs/000_Slices_for_ARA_registration/'
    out_path = os.path.join(general_path,
                            registration_file_path,
                            image_name + '.txt')

    return out_path
