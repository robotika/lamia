"""
  Copy & Paste from Parrot Bebop commands
  (possible usage also as parsing command log files)
  usage:
      ./commands.py <cmd log file>
"""
import time
import struct
from threading import Thread,Event,Lock
from collections import defaultdict

def moveCmd( speed, turn ):
    # ARCOMMANDS_ID_PROJECT_JUMPINGSUMO = 3,
    # ARCOMMANDS_ID_JUMPINGSUMO_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_JUMPINGSUMO_PILOTING_CMD_PCMD = 0,
    # flag - Boolean for "touch screen".
    # speed - [-100:100]
    # turn - [-100:100]
    return struct.pack("<BBHBbb", 3, 0, 0, (speed != 0 or turn != 0), speed, turn )

def jumpCmd( param ):
    # ARCOMMANDS_ID_PROJECT_JUMPINGSUMO = 3,
    # ARCOMMANDS_ID_JUMPINGSUMO_CLASS_ANIMATIONS = 2,    
    # ARCOMMANDS_ID_JUMPINGSUMO_ANIMATIONS_CMD_JUMP = 3,
    # param = enum[long, high]
    return struct.pack("<BBHI", 3, 2, 3, param )

def loadCmd():
    # ARCOMMANDS_ID_PROJECT_JUMPINGSUMO = 3,
    # ARCOMMANDS_ID_JUMPINGSUMO_CLASS_ANIMATIONS = 2,    
    # ARCOMMANDS_ID_JUMPINGSUMO_ANIMATIONS_CMD_JUMPLOAD = 2,
    return struct.pack("<BBH", 3, 2, 2 )

def postureCmd( param ):
    # param = enum[standing, jumper, kicker]
    # ARCOMMANDS_ID_PROJECT_JUMPINGSUMO = 3,
    # ARCOMMANDS_ID_JUMPINGSUMO_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_JUMPINGSUMO_PILOTING_CMD_POSTURE = 1,
    return struct.pack("<BBHI", 3, 0, 1, param )

def addCapOffsetCmd( offset ):
    "Add the specified offset to the current cap."
    # ARCOMMANDS_ID_PROJECT_JUMPINGSUMO = 3,
    # ARCOMMANDS_ID_JUMPINGSUMO_CLASS_PILOTING = 0,
    # ARCOMMANDS_ID_JUMPINGSUMO_PILOTING_CMD_ADDCAPOFFSET = 2,
    # offset Offset value in radians.
    return struct.pack("<BBHf", 3, 0, 2, offset )

def setVolumeCmd( volume ):
    "Master audio volume [0:100]"
    # ARCOMMANDS_ID_PROJECT_JUMPINGSUMO = 3,
    # ARCOMMANDS_ID_JUMPINGSUMO_CLASS_AUDIOSETTINGS = 12,
    # ARCOMMANDS_ID_JUMPINGSUMO_AUDIOSETTINGS_CMD_MASTERVOLUME = 0,
    return struct.pack("<BBHB", 3, 12, 0, volume )


def setDateCmd( date ):
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_COMMON = 4,
    # ARCOMMANDS_ID_COMMON_COMMON_CMD_CURRENTDATE = 1,
    # Date with ISO-8601 format
    return struct.pack("BBH", 0, 4, 1) + date.isoformat() + '\0'

def setTimeCmd( time ):    
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_COMMON = 4,
    # ARCOMMANDS_ID_COMMON_COMMON_CMD_CURRENTTIME = 2,
    # Time with ISO-8601 format
    # note, that "time.isoformat()" did not work '19:39:22.887000' milisec??
    return struct.pack("BBH", 0, 4, 2) + time.strftime("T%H%M%S+0000") + '\0'


def requestAllSettingsCmd():
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_SETTINGS = 2,
    # ARCOMMANDS_ID_COMMON_SETTINGS_CMD_ALLSETTINGS = 0
    return struct.pack("BBH", 0, 2, 0)


def requestAllStatesCmd():
    # ARCOMMANDS_ID_PROJECT_COMMON = 0,
    # ARCOMMANDS_ID_COMMON_CLASS_COMMON = 4,
    # ARCOMMANDS_ID_COMMON_COMMON_CMD_ALLSTATES = 0
    return struct.pack("BBH", 0, 4, 0)




def packData( payload, ackRequest=False ):
    frameType = 2
    if ackRequest:
        frameId = 11
    else:
        frameId = 10
    buf = struct.pack("<BBBI", frameType, frameId, 0, len(payload)+7)
    return buf + payload


class CommandSender( Thread ):
    "it is necessary to send PCMD with fixed frequency - Free Flight uses 40Hz/25ms"
    INTERNAL_COMMAND_PREFIX = chr(0x42)
    EXTERNAL_COMMAND_PREFIX = chr(0x33)
    def __init__( self, commandChannel, hostPortPair ):
        Thread.__init__( self )
        self.setDaemon( True )
        self.shouldIRun = Event()
        self.shouldIRun.set()
        self.lock = Lock()
        self.command = commandChannel
        self.hostPortPair = hostPortPair
        self.seqId = defaultdict( int )
        self.cmd = packData( moveCmd( 0, 0 ) )
        assert self.isPCMD( self.cmd )
        self.index = 0
        self.dropIndex = 7 # fake wifi problems

    def updateSeq( self, cmd ):
        "relace sequential byte based on 'channel'"
        assert len(cmd) > 3, repr(cmd)
        frameId = cmd[1]
        self.seqId[ frameId ] += 1
        return cmd[:2] + chr(self.seqId[frameId] % 256) + cmd[3:]

    def isPCMD( self, cmd ):
        if len(cmd) != 7+7: # BBHBbb
            return False
        return struct.unpack("BBH", cmd[7:7+4]) == (3, 0, 0)

    def send( self, cmd ):
        self.lock.acquire()
        self.command.separator( self.EXTERNAL_COMMAND_PREFIX )
        if cmd is not None:
            if self.isPCMD( cmd ):
                self.cmd = cmd
                self.command.separator( cmd ) # just store the command without sending it
            else:
                self.command.sendto( self.updateSeq(cmd), self.hostPortPair )
        self.command.separator( "\xFF" )
        self.lock.release()

    def run( self ):
        while self.shouldIRun.isSet():
            self.index += 1
            if self.dropIndex is None or self.index % self.dropIndex != 0:
                self.lock.acquire()
                self.command.separator( self.INTERNAL_COMMAND_PREFIX )
                self.command.sendto( self.updateSeq(self.cmd), self.hostPortPair )
                self.command.separator( "\xFF" )
                self.lock.release()
            time.sleep(0.025) # 40Hz

class CommandSenderReplay( CommandSender ):
    "fake class to replay synced messages"
    def __init__( self, commandChannel, hostPortPair, checkAsserts=True ):
        CommandSender.__init__( self, commandChannel, hostPortPair )
        self.checkAsserts = checkAsserts

    def start( self ):
        "block default Thread behavior"
        print "STARTED Replay"

    def send( self, cmd ):
        if not self.checkAsserts:
            # ignore input completely
            return

        prefix = self.command.debugRead(1)
        while prefix == self.INTERNAL_COMMAND_PREFIX:
            self.command.separator( self.updateSeq(self.cmd) ) # just verify command identity
            self.command.separator( "\xFF" )
            prefix = self.command.debugRead(1)
        assert prefix == self.EXTERNAL_COMMAND_PREFIX, hex(ord(prefix))

        if cmd is not None:
            if self.isPCMD( cmd ):
                self.cmd = cmd
                self.command.separator( cmd ) # just verify command identity
            else:
                self.command.sendto( self.updateSeq(cmd), self.hostPortPair )
        self.command.separator( "\xFF" )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print __doc__
        sys.exit(2)
    f = open(sys.argv[1], "rb")
    prefix = f.read(1)
    while len(prefix) > 0:
        print hex(ord(prefix))
        assert prefix in [CommandSender.INTERNAL_COMMAND_PREFIX, CommandSender.EXTERNAL_COMMAND_PREFIX]
        term = f.read(1)
        if term != "\xFF":
            header = term + f.read(6)
            frameType, frameId, seqId, totalLen = struct.unpack( "<BBBI", header )
            data = header + f.read( totalLen-7 )
            print " ".join(["%02X" % ord(x) for x in data])
            term = f.read(1)
        else:
            print "EMPTY"
        prefix = f.read(1)


# vim: expandtab sw=4 ts=4 

