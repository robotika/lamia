#!/usr/bin/python
"""
  Climbing stairs (demo for Tour-the-Stairs 2015)
  usage:
       ./stairs.py <task> [<metalog> [<F>]]
"""
import sys
import math

from jumpingsumo import JumpingSumo
from commands import moveCmd, jumpCmd, loadCmd, postureCmd, addCapOffsetCmd, setVolumeCmd

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

def move( robot, speed, steps ):
    for i in xrange(steps):
        robot.update( cmd=moveCmd(speed, 0) )
    robot.update( cmd=moveCmd(0,0) )

def step1( robot ):
#    move( robot, 20, 30 )
    move( robot, -20, 20 )
    robot.wait(1.0)
    robot.update( cmd=jumpCmd(1), ackRequest=True )
    robot.wait(5.0)
    move( robot, 20, 10 )
    move( robot, 0, 10 )
    move( robot, -20, 5 )
    robot.wait(1.0)

def step2( robot ):
    robot.update( cmd=jumpCmd(1), ackRequest=True )
    robot.wait(5.0)
    move( robot, 20, 20 )
    move( robot, -20, 5 )
    robot.update( cmd=addCapOffsetCmd(math.radians(10)) )

def backup( robot ):
    "fall back in order to save the sequence"
    robot.update( cmd=addCapOffsetCmd(math.radians(-180)) )
    move( robot, 20, 40 )
    robot.update( cmd=addCapOffsetCmd(math.radians(180)) )

def tourTheStairs2015( robot ):
    step1(robot)
    for i in xrange(3):
        step2(robot)
#            move( robot, -20, 3 )
    backup( robot )
    for i in xrange(10):
        step2(robot)


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
    tourTheStairs2015( robot )
    print "Battery:", robot.battery

# vim: expandtab sw=4 ts=4 

