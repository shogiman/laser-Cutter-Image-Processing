# -*- coding: utf-8 -*-
"""
Created on Sat Dec 28 13:40:07 2019

@author: Nicholas
"""

from   skimage import io
import glob
import pandas as pd
import numpy as np
import math

# import the dxf module
import ezdxf as dxf

config = {
    'width' : 10,
    'height': 150,
    
    # Config for including a central hole for connecting cut-outs
    'centreHoleIncluded'    : False,
    'centreHoleRadius'      : 0.05,  # Radius in mm
    'centreHoleRadiusLimit' : 0.05,  # Limit of main circle to centre hole...

    # Supported shapes 
    'triangle' : False,
    'circle'   : False,
    'square'   : True,

    # Config for curtaining the circles
    'curtainEnabled'    : False,
    
    # final width of image in cm
    'widthCm' :20,
    
    # Number  of circles in horizontal direction
    'numXCircles' : 40,
    
    # Flag to denote if boundary to be defined
    'boundaryCut' : True,

    # Max radius    
    'maxLineSize' : 255

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

def drawSquare(centreX, centreY, edgeLen):
    # Define containment box for curtains...
    offSet=edgeLen/2
    A = (centreX-offSet, centreY-offSet)
    B = (centreX-offSet, centreY+offSet)
    C = (centreX+offSet, centreY+offSet)
    D = (centreX+offSet, centreY-offSet)
    
    colorRed = 6 # red
    layer    = 'circles'
    weight   = 0.1
    
    msp.add_line(A, B, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
    msp.add_line(B, C, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
    msp.add_line(C, D, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
    msp.add_line(D, A, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
    
def calcRadius(actR, maxR):
    
    return actR

maxRadius=config['maxLineSize']

step = 5  # in mm
scaleFactor = 0.95 # coord scaling

widthCm=config['widthCm'] * scaleFactor


fileNames='*.png'
for image_path in sorted(glob.glob(fileNames)):
    print('Filename: {:s}'.format(image_path))
    
    image = io.imread(image_path, as_gray=True)
    #image=misc.face(gray=True)
    image=maxRadius-(image*maxRadius)    
    
    print(image.shape)
    print(image.dtype)

    # Start the creation of the dxf file to hold the png converted data
    doc = dxf.new(dxfversion='R2010')
    
    # Create new table entries (layers, linetypes, text styles, ...).
    doc.layers.new(name='circles', dxfattribs={'true_color': 0x00FFFFFF, 'lineweight':0.1})
    
    # DXF entities (LINE, TEXT, ...) reside in a layout (modelspace, 
    # paperspace layout or block definition).  
    msp = doc.modelspace()

    doc.header['$MEASUREMENT'] = 1 # metric
    doc.header['$INSUNITS']    = 4 # mm
    
    minIncrement=16
    numXCircles=config['numXCircles']
    increment=int(image.shape[1]/numXCircles)
    
    step = (widthCm*10)/numXCircles
    offS = step/2    
    
    incX=0
    incY=0
    
    rMin=255
    rMax=0
    
    spread=[]
    
    maxX=((image.shape[1]*step)/increment) -step   
    maxY=((image.shape[0]*step)/increment) - step
    yOffset = maxY
    
    for x in range(0,image.shape[1], increment):
            
        for y in range(0,image.shape[0], increment):
            
            if (image.shape[1] - x) >= increment:
                
                if (image.shape[0] - y) >= increment:         

                    radius = getAverage(image,x,y,increment)

                    # record the radious data
                    spread.append(radius)

                    if rMin > radius:
                        rMin = radius

                    if rMax < radius:
                        rMax = radius

                    limit = 0
                    drawCentreHole = False
                    
                    # Check whether centred hole is required
                    if config['centreHoleIncluded']:
                        coRadius = float(config['centreHoleRadius']) * scaleFactor
                        #print('c: {:.3f}     ch: {:.3f}'.format(actualRadius, coRadius))
                        if coRadius > 0:
                            drawCentreHole = True
                            limit = coRadius + config['centreHoleRadiusLimit']

                    maxRadiusArea = maxRadius * maxRadius #  no need to include pi
                    actRadiusArea = (maxRadiusArea * radius) / maxRadius 
                    actRadius     = math.sqrt(actRadiusArea)
                    actualRadius = ((step-1)*actRadius)/(2*maxRadius) # in mm

                    actualRadius *= scaleFactor 

                    if actualRadius > limit:

                        # now create cicle in output file
                        incX = (x/increment)*step
                        incY = yOffset - ((y/increment)*step)
                        
                        if drawCentreHole:
                            colorCo = 7
                            msp.add_circle((incX*step, incY*step), coRadius, dxfattribs={'layer': 'circles', 'color': colorCo, 'lineweight':0.1})           
    
                        colorGrey = 3
                        if config['circle']:             
                            msp.add_poly((incX, incY), actualRadius, dxfattribs={'layer': 'circles', 'color': colorGrey,'lineweight':0.1})

                        elif config['square']:             
                            drawSquare(incX, incY, actualRadius*2)

                        elif config['triangle']:             
                            msp.add_circle((incX, incY), actualRadius, dxfattribs={'layer': 'circles', 'color': colorGrey,'lineweight':0.1})
                        
        # create verical cuts for curtain effect        
        if config['curtainEnabled']:
             msp.add_line((incX, 0), (incX, maxY ), dxfattribs={'layer': 'circles', 'color': 5, 'lineweight':0.1})
             msp.add_circle((incX-offS, maxY+(step+offS)/2 ), float(config['centreHoleRadius']) * scaleFactor, dxfattribs={'layer': 'circles', 'color': 8, 'lineweight':0.1})
             msp.add_circle((incX-offS, 0-(step+offS)/2 ), float(config['centreHoleRadius']) * scaleFactor, dxfattribs={'layer': 'circles', 'color': 8, 'lineweight':0.1})
                              
    # Slice off curtains        
    if config['curtainEnabled']:

        # Add last hanger hole...
        msp.add_circle((incX+offS, maxY+(step+offS)/2 ), float(config['centreHoleRadius']) * scaleFactor, dxfattribs={'layer': 'circles', 'color': 8, 'lineweight':0.1})
        msp.add_circle((incX+offS, 0-(step+offS)/2 ), float(config['centreHoleRadius']) * scaleFactor, dxfattribs={'layer': 'circles', 'color': 8, 'lineweight':0.1})
    
    if config['boundaryCut'] or config['curtainEnabled']:    

        # Define containment box for curtains...
        A = (-step,     maxY+step)
        B = (incX+step, maxY+step)
        C = (incX+step, -step)
        D = (-step,     -step)
        
        colorRed = 6 # red
        layer    = 'circles'
        weight   = 0.1
        
        msp.add_line(A, B, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
        msp.add_line(B, C, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
        msp.add_line(C, D, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})
        msp.add_line(D, A, dxfattribs={'layer': layer, 'color': colorRed, 'lineweight':weight})

    
    # Now save the png's dxf file
    doc.saveas('{:s}_{:03d}cm_{:03d}cuts_curtain_{:s}.dxf'.format(image_path.split('.')[:-1][0], int(widthCm), numXCircles, str(config['curtainEnabled'])))
    print('Radius data:\n-----------\n    Min: {:d}\n    Max: {:d}'.format(rMin,rMax))

    

    # Display spread of average pixel colour            
    # spDf= pd.DataFrame(spread)
    # spDf.hist(bins=255)
    
