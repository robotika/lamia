#!/usr/bin/python
"""
  Climbing stairs (demo for Tour-the-Stairs 2015)
  usage:
       ./stairs_ver0.py <num stepss>
"""
import sys

import sumo # from https://github.com/haraisao/JumpingSumo-Python.git 
import time

def demo( numSteps ):
    cnt = sumo.SumoController('MyCtrl')
    cnt.connect()
    cnt.move(10)
    time.sleep(1.0)
    cnt.move(0)
    time.sleep(1.0)
    cnt.jump(1)
    time.sleep(3.0)
    cnt.terminate()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    demo( int(sys.argv[1]) )

# vim: expandtab sw=4 ts=4 

