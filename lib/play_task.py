# kevinlynx@gmail.com
import time, Queue
from async_http import AsyncHTTP
from threading import Thread
from log import logger

class PlayTask(Thread):
    GET_TIMEOUT = 2
    TIMEOUT = 1.0

    def __init__(self, queue, host, play_conf):
        Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self.host = host
        self.last_at = 0 # last query at
        self.last_send_at = 0
        self.play_idle_sum = 0
        self.query_idle_sum = 0
        self.next_q = None
        self.is_stop = False
        self.code_200_cnt = 0
        self.code_other_cnt = 0
        self.fail_cnt = 0
        self.ext_header = play_conf.get('http_header', {})
        timeout = play_conf.get('timeout', self.TIMEOUT * 1000) / 1000.0
        wait_count = play_conf.get('wait_count', 10000)
        cocurrency = play_conf.get('conn_pool_size', 500)
        self.http = AsyncHTTP(self.host, timeout, cocurrency, wait_count, self.ext_header)

    def start(self):
        self.http.start()
        Thread.start(self)

    # override
    def run(self):
        while not self.is_stop:
            self._play()
        logger.info('play task quit')

    def stop(self):
        self.is_stop = True
        self.http.stop()
        self.join(5)

    # only these primitiv type members, to prevent locking
    def stats(self):
        now = int(time.time() * 1000)
        delay = now - self.last_at
        io_stats = self.http.stats()
        return {'last_query_at': self.last_at,
            'query_delay': int(delay / 1000.0),
            'last_send_at': self.last_send_at,
            'code_200_cnt': self.code_200_cnt,
            'code_other_cnt': self.code_other_cnt,
            'fail_cnt': self.fail_cnt,
            'query_idle_sum': int(self.query_idle_sum / 1000.0),
            'play_idle_sum': int(self.play_idle_sum / 1000.0),
            'io': io_stats
        }

    def _play(self):
        if not self.next_q:
            self.next_q = self._safe_get()
        if not self.next_q: 
            return 
        if self.last_at > 0: # else the first time (just startup)
            self._make_idle()
        self._send(self.next_q)
        self.next_q = self._safe_get()

    def _make_idle(self):
        q_idle = self.next_q.tm - self.last_at
        self.query_idle_sum += q_idle
        idle = self.query_idle_sum - self.play_idle_sum
        if idle > 1000.0:
            logger.debug('idle (%d)ms > 1 sec', idle)
        if idle > 0:
            time.sleep(idle / 1000.0)

    def _safe_get(self):
        try:
            q = self.queue.get(True, self.GET_TIMEOUT)
            return q
        except Queue.Empty:
            logger.debug('get queue empty')
            return None

    def _send(self, q):
        self.last_at = q.tm
        now = int(time.time() * 1000)
        if self.last_send_at > 0:
            self.play_idle_sum += (now - self.last_send_at)
        self.last_send_at = now
        url = self._get_url(q.query)
        def callback(resp):
            if not resp: 
                self.fail_cnt += 1
            elif resp.status_code == 200:
                self.code_200_cnt += 1
            else:
                self.code_other_cnt += 1
        if not url:
            callback(None)
        else:
            self.http.get(url, callback)

    def _get_url(self, query): # FIXME
        try:
            return 'http://' + self.host + query
        except UnicodeDecodeError, e:
            pass
        return None

