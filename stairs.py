#!/usr/bin/python
"""
  Climbing stairs (demo for Tour-the-Stairs 2015)
  usage:
       ./stairs.py <task> [<metalog> [<F>]]
"""
import sys

from jumpingsumo import JumpingSumo
from commands import moveCmd, jumpCmd, loadCmd, postureCmd

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

def demo( robot ):
    for i in xrange(20):
        robot.update( cmd=moveCmd(10,0) )
    robot.update( cmd=moveCmd(0,0) )
#    robot.update( cmd=loadCmd() )
#    robot.wait(1.0)
#    print "posture"
#    robot.update( cmd=postureCmd(1), ackRequest=True )
    robot.wait(1.0)
    print "jump"
    robot.update( cmd=jumpCmd(1), ackRequest=True )
    robot.wait(3.0)

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

