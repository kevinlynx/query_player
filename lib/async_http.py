# kevinlynx@gmail.com
import gevent
from gevent import pool
from Queue import Queue
import threading, time, socket
from geventhttpclient import HTTPClient
from geventhttpclient.url import URL
from log import logger

__all__ = ['AsyncHTTP']

class MyGreenlet(gevent.Greenlet):
    def __init__(self, run = None, *args, **kwargs):
        gevent.Greenlet.__init__(self, run, *args, **kwargs)
        self.tm = int(time.time() * 1000)
    
class AsyncHTTP:

    # wait_io: qsize, in_io: qsize
    def __init__(self, host_full, timeout = 10, conn_pool_size = 1, qsize = 10000, headers = {}):
        vec = host_full.split(':')
        host = vec[0]
        port = int(vec[1])
        self.impl = HTTPClient(host, port = port,
            concurrency = conn_pool_size, network_timeout = timeout,
            connection_timeout = timeout)
        self.headers = headers
        self.qsize = qsize
        self.queue = Queue(self.qsize)
        self.tasks = None
        self.is_stop = False
        self.in_io = 0
        self.timeout = timeout
        self.thread = threading.Thread(target = self._loop)

    def start(self):
        self.thread.start()

    def stats(self):
        d = self.impl._connection_pool._semaphore.counter
        return {'wait_io': self.queue.qsize(), 'in_io': self.in_io, 'd': d}

    def stop(self):
        self.is_stop = True
        self.thread.join()

    def get(self, url_s, cb):
        self.queue.put((url_s, cb))

    def _loop(self):
        self.tasks = pool.Pool(self.qsize, MyGreenlet)
        while not self.is_stop:
            self._loop_once()

    def _loop_once(self):
        while len(self.tasks) < self.qsize and not self.queue.empty():
            url, cb = self.queue.get()
            self.tasks.spawn(lambda : self._do_get(url, cb))
        if len(self.tasks) > 0:
            self.in_io = self._run_io()
        else:
            time.sleep(0.01)

    def _run_io(self, timeout = 0.01):
        self.tasks.join(timeout, True)
        self._check_timeout()
        return len(self.tasks)

    def _do_get(self, url, cb):
        try:
            resp = self.impl.get(url, headers = self.headers) 
            cb(resp)
        except socket.timeout:
            cb(None)
        except socket.error:
            cb(None)
        except Exception, e:
            logger.warn('http exception: %r', e)
            cb(None)

    # task not executed in expected time, something wrong happened
    def _check_timeout(self):
        now = int(time.time() * 1000)
        to_kill = []
        for task in self.tasks.greenlets:
            if task.tm + 2 * 1000 * self.timeout < now:
                logger.warn('timeout task found %d ms', now - task.tm)
                to_kill.append(task)
        # target greenlet will receive exception
        for task in to_kill:
            self.tasks.killone(task, block = False)

if __name__ == '__main__':
    import time
    http = AsyncHTTP('127.0.0.1:3388')
    http.start()
    def cb(resp):
        print(resp.status_code)
        print(resp.read())
    http.get('http://127.0.0.1:3388/status', cb)
    time.sleep(2) 
    http.stop()

