#!/usr/bin/python
"""
  Stitching images
  usage:
       ./stitcher.py <input dir> <output dir>
"""
# Jumping Sumo images 640x480 with step 30deg
import sys
import math
import os
import cv2
import numpy

def stitcher( inDir, outDir ):
    result = None
    for name in os.listdir(inDir):
        print name
        img = cv2.imread( os.path.join(inDir, name) )
        img2 = img[100:380,240:400]
        if result is None:
            result = img2
        else:
            result = numpy.concatenate( (result, img2), axis=1 )
        cv2.imwrite( os.path.join(outDir, name), img2 )
    cv2.imwrite( os.path.join(outDir, "result.jpg"), result )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print __doc__
        sys.exit(2)
    stitcher( sys.argv[1], sys.argv[2] )

# vim: expandtab sw=4 ts=4 

