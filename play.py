#!/usr/bin/python
"""
  Replay Juming Sumo video from navdata
  usage:
       ./play.py <input navdata> [<step in ms> [<output file>]]
  
"""
import sys
import cv2
from video import *


def jpegGen( inputFile ):
    data = open(inputFile, "rb").read()
    vf = VideoFrames()
    while len(data) > 0:
        packet, data = cutPacket( data )
        if videoAckRequired( packet ):
            vf.append( packet )
        frame = vf.getFrame()
        if frame:
            yield frame


def playVideo( filename, timeStep=100, outFile=None ):
    writer = None
    if outFile:
        writer = cv2.VideoWriter( outFile, cv2.cv.CV_FOURCC('F', 'M', 'P', '4'), 10, (640,480) )    
    for frame in jpegGen( filename ):
        f = open("tmp.jpg", "wb")
        f.write(frame)
        f.close()
        img = cv2.imread("tmp.jpg")        
        if writer:
            writer.write( img )
        cv2.imshow('image', img)
        key = cv2.waitKey(timeStep)
        if key == 27: # ESC
            break
        if key > 0 and chr(key) in ['s', 'S']:
            cv2.imwrite( "frameX.jpg", frame )
    if writer:
        writer.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    filename = sys.argv[1]
    timeStamp = 100
    if len(sys.argv) > 2:
        timeStamp = int(sys.argv[2])
    outFile = None
    if len(sys.argv) > 3:
        outFile = sys.argv[3]
    assert "navdata" in filename, filename
    playVideo( filename, timeStamp, outFile )

# vim: expandtab sw=4 ts=4 

