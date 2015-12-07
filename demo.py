#!/usr/bin/python
"""
  Experiments with Jumping Sumo
  usage:
       ./demo.py <task> [<metalog> [<F>]]
"""
import sys
import math

from jumpingsumo import JumpingSumo
from commands import moveCmd, jumpCmd, loadCmd, postureCmd, addCapOffsetCmd, setVolumeCmd

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException


g_lastImage = None
def keepLastImage( frame, debug=False ):
    global g_lastImage
    g_lastImage = frame[2]

def demo( robot ):
    "panoramatic picture"
    DEG_STEP = 30
    robot.setVideoCallback( keepLastImage )
    for absAngle in xrange(0, 360, DEG_STEP):
        robot.update( cmd=addCapOffsetCmd(math.radians(DEG_STEP)) )
        robot.wait(1.0)
        assert g_lastImage is not None
        open( "scan%03d.jpg" % absAngle, "wb" ).write( g_lastImage )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    metalog=None
    if len(sys.argv) > 2:
        metalog = MetaLog( filename=sys.argv[2] )
    if len(sys.argv) > 3 and sys.argv[3] == 'F':
        disableAsserts()

    robot = JumpingSumo( metalog=metalog )    
    demo( robot )
    print "Battery:", robot.battery

# vim: expandtab sw=4 ts=4 

