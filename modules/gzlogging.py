from modules.basemodule import BaseModule

import gzip
import subprocess


class GzLogging(BaseModule):
    def __init__(self, mud, logfname):
        self.logfname = logfname
        self.file = gzip.open(logfname, 'a', buffering=1)
        super().__init__(mud)

    def quit(self):
        self.file.close()

    def alias(self, line):
        if line.startswith('#grep '):
            arg = line[len('#grep '):]
            grep = subprocess.Popen(['/bin/sh', '-c', 'tail -n10000 {} | grep -a {}'.format(self.logfname, arg)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = grep.communicate(timeout=5)
            self.mud.log('\n' + out.decode('utf-8'))
            return True
        self.file.write('> ' + line + '\n')

    def trigger(self, raw, stripped):
        self.file.write(raw + '\n')
