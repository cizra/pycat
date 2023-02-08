from modules.basemodule import BaseModule
import collections
import json
import os
import pprint
import re
import shutil
import time


def log(*args, **kwargs):
    print(*args, **kwargs)


class CommLog(BaseModule):
    def __init__(self, mud, commfname):
        super().__init__(mud)
        self.fname = commfname


    # def drawMapToFile(self):
    #     with open('map.txt', 'wt') as f:
    #         f.write(self.draw())

    def handleGmcp(self, cmd, value):
        if cmd == 'comm.channel':
            channel = value['chan']
            msg = value['msg']
            player = value['player']
            log("Got comm.channel with {}".format(msg))
            self.write(msg)

    def write(self, msg):
        with open(self.fname, 'a') as f:
            f.write(msg + '\n')

