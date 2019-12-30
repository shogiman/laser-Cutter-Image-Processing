# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 13:40:07 2019

@author: Nicholas
"""

from   skimage import io
import glob
import pandas as pd

# import the dxf module
import ezdxf as dxf

config = {
    'width' : 10,
    'height': 150
    }

def getAverage(matrix, x, y, sz=16):
    
    val = 0
    cnt = 0
    szx=sz

    if (x + szx) >= matrix.shape[1]:
        szx = matrix.shape[1] - x
    
    szy=sz
    if (y + szy) >= matrix.shape[0]:
        szy = matrix.shape[0] - y

    for xVal in range(x,x+sz):
        for yVal in range(y,y+sz):
            val += matrix[yVal,xVal]
            cnt +=1
            
    res = int(val/cnt)

    #print('Vals: ({:d}, {:d}) --> {:s}  av: {:d}'.format(x,y, str(matrix.shape),res))
    
    return res



maxRadius=255

step = 5  # in mm
scaleFactor = 0.95 # coord scaling

widthCm=20 * scaleFactor

yOffset=0

fileNames='*.png'
for image_path in sorted(glob.glob(fileNames)):
    print('Filename: {:s}'.format(image_path))
    
    image = io.imread(image_path, as_gray=True)
    #image=misc.face(gray=True)
    image=maxRadius-(image*maxRadius)    
    
    '''
    threshVal = filters.threshold_otsu(image)
    ni = image.copy()
    np.putmask(ni, ni<threshVal, 0)
    
    plt.figure(figsize=(7, 3))
    
    plt.subplot(121)
    plt.imshow(ni, cmap='gray', interpolation='nearest')
    '''

    #d=image[0]
    # Y = 0.2125 R + 0.7154 G + 0.0721 B
    
    print(image.shape)
    print(image.dtype)

    # Start the creation of the dxf file to hold the png converted data
    doc = dxf.new(dxfversion='R2010')
    
    # Create new table entries (layers, linetypes, text styles, ...).
    doc.layers.new(name='circles', dxfattribs={'true_color': 0x00FFFFFF, 'lineweight':1})
    
    # DXF entities (LINE, TEXT, ...) reside in a layout (modelspace, 
    # paperspace layout or block definition).  
    msp = doc.modelspace()

    minIncrement=16
    numXCircles=60
    increment=int(image.shape[1]/numXCircles)
#    if increment < minIncrement:
#        increment = minIncrement
    
    step = (widthCm*10)/numXCircles
    
    incX=0
    incY=0
    
    rMin=255
    rMax=0
    
    spread=[]
    
    for x in range(0,image.shape[1], increment):
        
        for y in range(0,image.shape[0], increment):
            
            if (image.shape[1] - x) >= increment:
                
                if (image.shape[0] - y) >= increment:         

                    radius = getAverage(image,x,y,increment)

                    # rercord the radious data
                    spread.append(radius)

                    if rMin > radius:
                        rMin = radius

                    if rMax < radius:
                        rMax = radius

                    limit = 0
                    if radius > limit:
        
                        actualRadius = ((step-1)*radius)/(2*maxRadius) # in mm
                        actualRadius *= scaleFactor 
                        
                        # now create cicle in output file
                        incX = x/increment
                        incY = yOffset - (y/increment)
                        msp.add_circle((incX*step, incY*step), actualRadius, dxfattribs={'layer': 'circles','lineweight':1})
            
  
                
    # Now save the png's dxf file
    doc.saveas('{:s}.dxf'.format(image_path.split('.')[:-1][0]))
    print('Radius data:\n-----------\n    Min: {:d}\n    Max: {:d}'.format(rMin,rMax))

    # Display spread of average pixel colour            
    spDf= pd.DataFrame(spread)
    spDf.hist(bins=255)
    
