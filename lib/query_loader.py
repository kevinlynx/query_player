# kevinlynx@gmail.com
import time
import Queue
from threading import Thread
import query_parser
from log import logger

class FileLoader:
    def __init__(self, file):
        with open(file) as f:
            self.lines = f.readlines()

    def load(self):
        lines = self.lines
        self.lines = []
        return lines

class QueryLoader(Thread):
    PUT_TIMEOUT = 5

    def __init__(self, queue, impl, load_conf):
        Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self.impl = impl
        self.parse_fn = load_conf['parser'] if load_conf.has_key('parser') else None
        self.is_stop = False
        self.wait_put = []
        self.wait_idx = 0
        self.total = 0
        self.last_load_at = 0

    def start(self):
        self.impl.start()
        Thread.start(self)

    def stop(self):
        self.impl.stop()
        self.is_stop = True
        self.join(5)

    def stats(self):
        return {'total': self.total, 'last_load_at': self.last_load_at}

    # override
    def run(self):
        while not self.is_stop:
            if self._run_once() == 0:
                time.sleep(0.01)
        logger.info('query loader quit')

    def _run_once(self):
        self._do_load()
        put_start = self.wait_idx
        for i in range(self.wait_idx, len(self.wait_put)):
            line = self.wait_put[i]
            q = query_parser.parse(self.parse_fn, line)
            if not q: continue
            if not self._safe_put(q):
                break
            self.wait_idx += 1
        return self.wait_idx - put_start

    def _do_load(self):
        if self.wait_idx >= len(self.wait_put):
            self.wait_put = self.impl.load()
            self.wait_idx = 0
            self.last_load_at = int(time.time() * 1000)

    def _safe_put(self, q):
        try:
            self.queue.put(q, True, self.PUT_TIMEOUT) 
            self.total += 1
        except Queue.Full:
            logger.warn('put queue full')
            return False
        return True

if __name__ == '__main__':
    pass
