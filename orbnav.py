#!/usr/bin/python
"""
  Experiments with SURFnav, well replaced by ORB descriptors -> orbnav
  usage:
       ./orbnav.py <input dir>
"""
import sys
import math
import os
import cv2
import numpy as np

# http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_surf_intro/py_surf_intro.html
# note:
# SURF is good at handling images with blurring and rotation, but not good at handling viewpoint change and illumination change.
# or maybe use ORB instead:
# ORB: An efficient alternative to SIFT or SURF in 2011
# SIFT and SURF are patented and you are supposed to pay them for its use. But ORB is not !
# http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_feature2d/py_orb/py_orb.html

# workaround taken from
#    http://stackoverflow.com/questions/20259025/module-object-has-no-attribute-drawmatches-opencv-python
def drawMatches(img1, kp1, img2, kp2, matches):
    """
    My own implementation of cv2.drawMatches as OpenCV 2.4.9
    does not have this function available but it's supported in
    OpenCV 3.0.0

    This function takes in two images with their associated 
    keypoints, as well as a list of DMatch data structure (matches) 
    that contains which keypoints matched in which images.

    An image will be produced where a montage is shown with
    the first image followed by the second image beside it.

    Keypoints are delineated with circles, while lines are connected
    between matching keypoints.

    img1,img2 - Grayscale images
    kp1,kp2 - Detected list of keypoints through any of the OpenCV keypoint 
              detection algorithms
    matches - A list of matches of corresponding keypoints through any
              OpenCV keypoint matching algorithm
    """

    # Create a new output image that concatenates the two images together
    # (a.k.a) a montage
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

    # Place the first image to the left
    out[:rows1,:cols1] = np.dstack([img1, img1, img1])

    # Place the next image to the right of it
    out[:rows2,cols1:] = np.dstack([img2, img2, img2])

    # For each pair of points we have between both images
    # draw circles, then connect a line between them
    for mat in matches:

        # Get the matching keypoints for each of the images
        img1_idx = mat.queryIdx
        img2_idx = mat.trainIdx

        # x - columns
        # y - rows
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Draw a small circle at both co-ordinates
        # radius 4
        # colour blue
        # thickness = 1
        cv2.circle(out, (int(x1),int(y1)), 4, (255, 0, 0), 1)   
        cv2.circle(out, (int(x2)+cols1,int(y2)), 4, (255, 0, 0), 1)

        # Draw a line in between the two points
        # thickness = 1
        # colour blue
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), (255, 0, 0), 1)


    # Show the image
    cv2.imshow('Matched Features', out)
    cv2.waitKey(0)
    cv2.destroyWindow('Matched Features')

    # Also return the image if you'd like a copy
    return out


def orbnav( inDir ):
    result = None
    orb = cv2.ORB()
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    img1, kp1, des1 = None, None, None
    for name in os.listdir(inDir):
        print name
        img2 = cv2.imread( os.path.join(inDir, name) )
        kp2, des2 = orb.detectAndCompute(img2, None)
        print len(kp2)
        if img1 is not None:
            matches = bf.match(des1,des2)
            matches = sorted(matches, key = lambda x:x.distance)
            gray1 = cv2.cvtColor( img1, cv2.COLOR_BGR2GRAY )
            gray2 = cv2.cvtColor( img2, cv2.COLOR_BGR2GRAY )
            img3 = drawMatches(gray1,kp1,gray2,kp2,matches[:10])
            cv2.imwrite( "tmp.jpg", img3 )
        img1, kp1, des1 = img2, kp2, des2

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    orbnav( sys.argv[1] )

# vim: expandtab sw=4 ts=4 

