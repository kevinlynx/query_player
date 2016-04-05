# kevinlynx@gmail.com
# StarAgent
import os, time
import common
from log import logger

__all__ = ['LoaderImpl']

# because of staragent secure reason
# open a proxy on remote machine which can be ssh
class RemoteAgent:
    SELF_PATH = os.path.split(os.path.realpath(__file__))[0]
    PROXY_FILE = SELF_PATH + '/../sh/*'
    DST_PATH = '/tmp/'
    DST_BIN = '/tmp/star_proxy.sh'

    def __init__(self, host, aport, rport):
        self.host = host
        self.aport = aport
        self.rport = rport

    def start(self):
        common.run_cmd('scp %s %s:%s' % (self.PROXY_FILE, self.host, self.DST_PATH))
        common.run_cmd(self._format_start_cmd(), nonblock = True)
        time.sleep(1)

    def stop(self):
        common.run_cmd(self._format_stop_cmd())

    def _format_start_cmd(self):
        cmd = self.DST_BIN + ' start %d' % self.rport
        return 'ssh %s %s' % (self.host, cmd)

    def _format_stop_cmd(self):
        cmd = self.DST_BIN + ' stop %d' % self.rport
        return 'ssh %s %s' % (self.host, cmd)

class LoaderImpl:
    INTERVAL = 2
    # don't skip logs, otherwise the consumer (player task) may sleep for a long time!
    EXP_TIME = 60 * 60 * 24
    TASK_ID = 'query_player'
    APORT = 8182
    RPORT = 18182

    def __init__(self, args):
        def get(k, d): return args[k] if args.has_key(k) else d
        self.host = get('host', '127.0.0.1:%d' % self.APORT)
        self.file = args['file']
        self.taskid = get('taskid', LoaderImpl.TASK_ID)
        self.last_at = 0
        if self.host.startswith('127.0.0.1') or self.host.startswith('localhost'):     
            self.agent = None
        else:
            vec = self.host.split(':')
            ip = vec[0]
            port = int(vec[1])
            self.host = ip + ':' + str(self.RPORT)
            self.agent = RemoteAgent(ip, port, self.RPORT)

    def start(self):
        if self.agent: self.agent.start()
        self._skip_to_end()

    def stop(self):
        if self.agent: self.agent.stop()

    def load(self):
        now = time.time()
        if now - self.last_at < self.INTERVAL:
            return []
        self.last_at = now
        url = self._get_url()
        resp = common.http_get(url, 1.0)
        return filter(lambda i: len(i) > 0, resp.split('\n'))

    def _get_url(self, hungry = False, size = 20):
        hs = 'true' if hungry else 'false'
        return 'http://' + self.host + '/tail?task_id=%s&file=%s&hungry=%s&exptime=%d&maxsize=%d' \
            % (self.taskid, self.file, hs, self.EXP_TIME, size)

    def _skip_to_end(self):
        common.http_get(self._get_url(True, 1), 1.0)

if __name__ == '__main__':
    import time
    impl = LoaderImpl({'file': '/home/admin/sp_mini/logs/access_log_sp',
        'host': '127.0.0.1:8182'
    })
    impl.start()
    time.sleep(2)
    list = impl.load()
    print(list[0])
    print(list[-1])
    impl.stop()

