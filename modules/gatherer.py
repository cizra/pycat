from modules.basemodule import BaseModule

import random
import re
import time


def lagSend(mud, lag, cmd):
    mud.log("Enqueueing " + cmd + " @ " + str(lag))
    def logAndSend(cmd):
        mud.log("laggy send " + cmd)
        mud.send(cmd)
    mud.timers["lagsend_" + cmd] = mud.mkdelay(lag, lambda m, cmd=cmd: logAndSend(cmd))

class Gatherer(BaseModule):
    def getTriggers(self):
        return {
            '^A fallow deer nibbles on the leaves of a bush\.': 'kill fallow',
            '^A doe looks up as you happen along\.$': 'kill doe',
            '^A buck looks up as you happen along\.$': 'kill buck',
            '^(A|An|The) (.+) is DEAD!!!$': 'butcher corpse', # TODO: trigger on combat end
            '^You manage to skin and chop up the body of (.+)\.$': 'get all.leather',
            '^You are done skinning and butchering the body of (.+)\.$': 'look',
            }

def getClass():
    return Gatherer
