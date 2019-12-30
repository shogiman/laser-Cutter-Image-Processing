This file will parse all **.png** files in the current working directory and generate a **.dxf** corresponding to each **.png** file.
The script works on the following principle:

 * The input file is broken down into a confgirable number of square blocks (default 60 in x-axis), approximating a configurable width in cm (default 20cm).
 * The average greyscaly colour for the pixels in that square block is calculated
 * A circle is drawn, in the output **.dxf** file coresponding to the average value returned
 
 The resulting **.dxf** file contains an image, not unlike the old newspaper black and whites pictures that have large dots for dark areas and small dots for light areas
 
