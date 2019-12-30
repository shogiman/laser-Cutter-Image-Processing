# laser-Cutter-Image-Processing
This is a series of files (both programs and images) I am using for use with a laser cutter I have access to

The conversion  of image files into **.dxf** files that I can use with a laser cutter requires some pre-processing of image files.  I primarily use **.png** files and any sripts I use tend to reference only those files, though with a little tweaking I am sure the scripts can be altered to accomodate other file formats.

Initially this repository shall contain the following types of files:
 * Python files for image processing
 * **.png** files that I have generated (for subsequent pre-processing)
 * **.dxf** files I have created, for importing into the laser cutter software (dongled to the machine in question)

**pictureLaserCut.py**

This file will parse all .png files in the current working directory and generate a .dxf corresponding to each .png file. The script works on the following principle

 * The input file is broken down into a confgirable number of square blocks (default 60 in x-axis)
 * The width of the final graphic is approximating a configurable width in cm (default 20cm).
 * The average greyscaly colour for the pixels in that square block is calculated
 * A circle is drawn, in the output .dxf file coresponding to the average value returned

The resulting .dxf file contains an image, not unlike the old newspaper black and whites pictures that have large dots for dark areas and small dots for light areas

__Pre-requisites:__
 * import skimage
 * import glob
 * import pandas
 * import ezdxf
