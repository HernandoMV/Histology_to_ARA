# Histology_to_ARA
Registration of a brain slice to the Allen Reference Atlas

## Dependencies
- mobie beta (expert usage version) from https://github.com/mobie/mobie-viewer-fiji


## Steps
1. In MoBIE, load the ARA (TODO: create instructions for how to)
2. Select plane corresponding to histology
3. Log transformation and copy to .txt file
4. Create screenshot WITH DEFAULT PARAMETERS. For 25um/pixel atlas this is 22.619um/px
5. Register the histology to screenshot (elastix: TODO: code this for multiple slices)
6. Transform (2D to 2D) points of interest using transformix (TODO)
7. Transform (2D to 3D) points to ARA (e.g. python register_2D_to_3D.py 135 178 25 /mnt/c/Users/herny/Desktop/Reg_test/mobie_position.txt)
