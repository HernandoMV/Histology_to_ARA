#!/usr/bin/python
# # First, calling register_2D_to_2D.py
# Second, calling register_2D_to_3D.py

from functions.register_2D_to_2D import register_2D_to_2D_transformix
from functions.register_2D_to_3D import register_2D_to_3D_affine
import functions.general_functions as gf
import sys
import os
import pandas as pd
import numpy as np


def points_to_ARA(path_to_dataframe, resolution=25):
    '''
    This script transforms points (outputs from Inmuno_4channels_analysis.ipynb in
    CellProfiler_AnalysisPipelines) to the 3D atlas in two steps

    param path_to_dataframe: absolute path to the dataframe
    param resolution: resolution of ARA in um/px
    returns: nothing, it saves a .csv file in the same directory as the input
    '''
    # check that file exists
    assert os.path.isfile(path_to_dataframe), 'file does not exist'

    # read input from the notebook
    df = pd.read_pickle(path_to_dataframe)

    # get the registration image core name for every row
    df['reg_im_corename'] = df.apply(gf.make_reg_core_name_from_series, axis=1)

    # get the positions of the cells in the downsample image (the one used for registration)
    df_tr = gf.get_prereg_coordinates(df)

    # create two columns to hold data
    df_tr['x_coord_post'] = np.nan
    df_tr['y_coord_post'] = np.nan
    df_tr['z_coord_post'] = np.nan

    # for each image
    ind_images = df_tr.reg_im_corename.unique()
    # iterate over each manually draw roi
    for imname in ind_images:
        # get the indexes of the cells belonging to that image
        sub_idx = df_tr[df_tr.reg_im_corename == imname].index.values
        # get path to transformation file
        trans_file_path = gf.get_transformation_file_path(df_tr.attrs['datapath'], imname)
        # get the xs and ys values
        xs_2d = list(df_tr.loc[sub_idx].x_coord_pre)
        ys_2d = list(df_tr.loc[sub_idx].y_coord_pre)
        # apply transformix
        tr_2d = register_2D_to_2D_transformix(xs_2d, ys_2d, trans_file_path)

        # get their positions in the 3D space
        if tr_2d is not None:  # transformix was successful
            xs_tr_2d = [i[0] for i in tr_2d]
            ys_tr_2d = [i[1] for i in tr_2d]
            # get the mobie position file
            mobie_file_path = gf.get_mobie_file_path(df_tr.attrs['datapath'], imname)
            # apply 2D to 3D transformation
            tr_3d = register_2D_to_3D_affine(xs_tr_2d, ys_tr_2d, resolution, mobie_file_path)
            # update columns
            df_tr.at[sub_idx, 'x_coord_post'] = [i[0] for i in tr_3d]
            df_tr.at[sub_idx, 'y_coord_post'] = [i[1] for i in tr_3d]
            df_tr.at[sub_idx, 'z_coord_post'] = [i[2] for i in tr_3d]

    # create a new column with the indexes of the cells (for checking them if needed)
    df_tr['cell_index'] = df_tr.index.values
    # subselect dataframe
    df_tr = df_tr[['x_coord_post', 'y_coord_post', 'z_coord_post', 'cell_label', 'cell_index']]
    # save output as csv
    outpath = os.path.dirname(path_to_dataframe)
    fbasename = os.path.splitext(os.path.basename(path_to_dataframe))[0]
    file_out_path = os.path.join(outpath, '_'.join([fbasename, 'ARA_coordinates.csv']))
    df_tr.to_csv(file_out_path, index=False)


if __name__ == '__main__':
    # check input
    if len(sys.argv) not in [2, 3]:
        sys.exit('Incorrect number of arguments, please run like this:\
            python points_transformation path_to_dataframe optional:resolution_of_ARA')
    # catch input
    inpath = sys.argv[1]
    if len(sys.argv) == 3:
        res = sys.argv[2]
        # run function
        points_to_ARA(path_to_dataframe=inpath, resolution=res)
    else:
        points_to_ARA(path_to_dataframe=inpath)
