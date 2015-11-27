#!/usr/bin/python
"""
  Basic class for communication to Parrot Jumping Sumo (based on Bebop/Katarina)
"""
import sys
import socket
import datetime
import struct
import time

from navdata import *
from commands import *
from video import VideoFrames

# this will be in new separate repository as common library fo robotika Python-powered robots
from apyros.metalog import MetaLog, disableAsserts
from apyros.manual import myKbhit, ManualControlException

HOST = "192.168.2.1" # Katarina: "192.168.42.1"
DISCOVERY_PORT = 44444

NAVDATA_PORT = 43210 # d2c_port
COMMAND_PORT = 54321 # c2d_port

class JumpingSumo:
    def __init__( self, metalog=None, onlyIFrames=True ):
        if metalog is None:
            self._discovery()
            metalog = MetaLog()
        self.navdata = metalog.createLoggedSocket( "navdata", headerFormat="<BBBI" )
        self.navdata.bind( ('',NAVDATA_PORT) )
        if metalog.replay:
            self.commandSender = CommandSenderReplay(metalog.createLoggedSocket( "cmd", headerFormat="<BBBI" ), 
                    hostPortPair=(HOST, COMMAND_PORT), checkAsserts=metalog.areAssertsEnabled())
        else:
            self.commandSender = CommandSender(metalog.createLoggedSocket( "cmd", headerFormat="<BBBI" ), 
                    hostPortPair=(HOST, COMMAND_PORT))
        self.console = metalog.createLoggedInput( "console", myKbhit ).get
        self.metalog = metalog
        self.buf = ""
        self.videoFrameProcessor = VideoFrames( onlyIFrames=onlyIFrames, verbose=False )
        self.videoCbk = None
        self.videoCbkResults = None
        self.battery = None
        self.flyingState = None
        self.flatTrimCompleted = False
        self.manualControl = False
        self.time = None
        self.altitude = None
        self.position = (0,0,0)
        self.speed = (0,0,0)
        self.positionGPS = None
        self.cameraTilt, self.cameraPan = 0,0
        self.lastImageResult = None
        self.navigateHomeState = None
        self.config()
        self.commandSender.start()
        
    def _discovery( self ):
        "start communication with the robot"
        filename = "tmp.bin" # TODO combination outDir + date/time
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        s.connect( (HOST, DISCOVERY_PORT) )
        s.send( '{"controller_type":"computer", "controller_name":"lamia", "d2c_port":"43210"}' )
        f = open( filename, "wb" )
        while True:
            data = s.recv(10240)
            if len(data) > 0:
                f.write(data)
                f.flush()
                break
        f.close()
        s.close()

    def _update( self, cmd ):
        "internal send command and return navdata"
        
        if not self.manualControl:
            self.manualControl = self.console()
            if self.manualControl:
                # raise exception only once
                raise ManualControlException()

        # send even None, to sync in/out queues
        self.commandSender.send( cmd )

        while len(self.buf) == 0:
            data = self.navdata.recv(240960)
            self.buf += data
        data, self.buf = cutPacket( self.buf )
        return data

    def _parseData( self, data ):
        try:
            parseData( data, robot=self, verbose=False )
        except AssertionError, e:
            print "AssertionError", e


    def update( self, cmd=None, ackRequest=False ):
        "send command and return navdata"
        if cmd is None:
            data = self._update( None )
        else:
            data = self._update( packData(cmd, ackRequest=ackRequest) )
        while True:
            if ackRequired(data):
                self._parseData( data )
                data = self._update( createAckPacket(data) )
            elif pongRequired(data):
                self._parseData( data ) # update self.time
                self.commandSender.send( cmd=createPongPacket(data) )
                return None # interrupt update routines
            elif videoAckRequired(data):
                if self.videoCbk:
                    self.videoFrameProcessor.append( data )
                    frame = self.videoFrameProcessor.getFrameEx()
                    if frame:
                        self.videoCbk( frame, debug=self.metalog.replay )
                    if self.videoCbkResults:
                        ret = self.videoCbkResults()
                        if ret is not None:
                            print ret
                            self.lastImageResult = ret
                data = self._update( createVideoAckPacket(data) )
            else:
                break
        self._parseData( data )
        return data


    def setVideoCallback( self, cbk, cbkResult=None ):
        "set cbk for collected H.264 encoded video frames & access to results queue"
        self.videoCbk = cbk
        if cbkResult is None:
            self.videoCbkResults = None
        else:
            self.videoCbkResults = self.metalog.createLoggedInput( "cv2", cbkResult ).get
        

    def config( self ):
        # initial cfg
        dt = self.metalog.now()
        if dt: # for compatibility with older log files
            self.update( cmd=setDateCmd( date=dt.date() ) )
            self.update( cmd=setTimeCmd( time=dt.time() ) )
        self.update( cmd=requestAllStatesCmd() )
        self.update( cmd=requestAllSettingsCmd() )


    def wait( self, duration ):
        print "Wait", duration
        assert self.time is not None
        startTime = self.time
        while self.time-startTime < duration:
            self.update()

# vim: expandtab sw=4 ts=4 

