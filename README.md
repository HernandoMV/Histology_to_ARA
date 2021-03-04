# Histology_to_ARA
Registration of a brain slice to the Allen Reference Atlas

## Dependencies
- mobie beta (expert usage version) from https://github.com/mobie/mobie-viewer-fiji


## Steps
### 1. In MoBIE, load the ARA (Use Mobie (see above) in expert mode)
####  1.1. Select plane corresponding to histology
####  1.2. Log transformation and copy to .txt file
####  1.3. Create screenshot WITH DEFAULT PARAMETERS. For 25um/pixel atlas this is 22.619um/px
####  1.4. Save text file and screenshot with the same names (ending in '.txt' and  '_ARA.txt' as the histology in the same folder)
### 2. Register the histology to screenshot (e.g. python folder_register_ARA_to_histology.py 'path_to_000_Slices_for_ARA_registration')
### 3. Transform (2D to 3D) points to ARA (e.g. python points_transformation 'path_to_dataframe')
This dataframe is generated with Inmuno_4channels_analysis.ipynb in CellProfiler_AnalysisPipelines - https://github.com/HernandoMV/CellProfiler_AnalysisPipelines

