# kevinlynx@gmail.com
# load a local file
import os, time
import common
from log import logger

__all__ = ['LoaderImpl']

'''
args: {'file': 'absolute path to file'}
'''
class LoaderImpl:
    LINES = 3000

    def __init__(self, args):
        self.name = args['file']
        self.fp = None
        self.ino = 0
        self.half_line = None

    def start(self):
        self._open()

    def stop(self):
        self._close()

    def load(self):
        if not self.fp: return []
        lines = []
        for i in xrange(0, self.LINES):
            line = self.fp.readline()
            if len(line) > 0 and not line.endswith('\n'):
                self.half_line = line
                break
            if line and self.half_line:
                line = self.half_line + line.strip()
                self.half_line = None
            else:
                line = line.strip()
            if not line: 
                self._check_rotated()
                return lines
            lines.append(line)
        return lines

    def _check_rotated(self):
        try:
            if os.stat(self.name).st_ino != self.ino:
                logger.info('file rotated %s', self.name)
                self._close() 
                self._open()
        except OSError, e:
            pass

    def _open(self):
        try:
            self.fp = open(self.name, 'r')
            self.fp.seek(0, 2)
            self.ino = os.fstat(self.fp.fileno()).st_ino
        except IOError, e:
            logger.warn('open local file [%s] failed', self.name)

    def _close(self):
        if self.fp: 
            self.fp.close()
            self.fp = None 
            self.ino = 0

if __name__ == '__main__':
    import time
    loader = LoaderImpl({'file': '/home/admin/sp_mini/logs/access_log_sp'})
    loader.start()
    time.sleep(2)
    lines = loader.load()
    print(lines[-1])
    time.sleep(2)
    lines = loader.load()
    print(lines[0])
    loader.stop()

