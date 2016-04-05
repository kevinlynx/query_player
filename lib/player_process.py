# kevinlynx@gmail.com
# player in a standalone process
from multiprocessing import Process, Pipe
from player import Player
from log import logger
import common

class PlayerProcess(Process):
    def __init__(self, conn_p, conn_c, pargs, conf):
        def get(args, k, d = None, ex = False): 
            if ex and not args.has_key(k): raise ValueError('require %s' % k)
            return args[k] if args.has_key(k) else d
        loader_args = get(pargs, 'loader', ex = True)
        name = get(pargs, 'name', ex = True)
        Process.__init__(self, name = name)
        self.daemon = True
        m = __import__(get(loader_args, 'name', ex = True))
        impl = m.LoaderImpl(get(loader_args, 'args', None))
        self.conn_c = conn_c
        self.conn_p = conn_p
        self.player = Player(get(pargs, 'host', ex = True), impl, 
            conf['loader'], conf['player'],
            get(pargs, 'qsize', 1000))

    def stop(self):
        self.conn_p.send(('quit', None))
        self.join(1)

    def stats(self):
        self.conn_p.send(('stats', None))
        if self.conn_p.poll(0.005):
            return self.conn_p.recv()
        return self._stats()

    def run(self):
        self.player.start()
        self._safe_run()
        self.player.stop()

    def _safe_run(self):
        while True:
            try:
                msg, args = self.conn_c.recv()
                if msg == 'quit':
                    break            
                elif msg == 'stats':
                    self.conn_c.send(self._stats())
            except (KeyboardInterrupt, SystemExit):
                break

    def _stats(self):
        return {'pid': self.pid, 'name': self.name, 'player': self.player.stats()}

'''
args:
[
    {
    'name': 'player1',
    'host': '10.181.97.3:3388',
    'qsize': 1000,
    'loader': {
        'name': 'loader_star',
        'args': {
            'host': '127.0.0.1:8182',
            'file': '/home/admin/sp_mini/logs/access_log_sp'
        }
    }},
    ...
'''
class MultiPlayer:
    def __init__(self, args, conf):
        if len(args) == 0: raise RuntimeError('no player configed')
        self.players = self._create(args, conf)
        self.confs = args
        self.global_conf = conf
         
    def start(self):
        for (_, player) in self.players.items():
            player.start()

    def stop(self):
        for (_, player) in self.players.items():
            player.stop()

    def append(self, arg):
        if self.players.has_key(arg['name']): 
            logger.debug('player %s exists', arg['name'])
            return False
        try:
            player = self._create_one(arg, self.global_conf)
            player.start()
            self.players[player.name] = player
            self.confs.append(arg)
        except ImportError, e:
            logger.warn('create player failed of invalid loader: %r', e)
            return False
        except ValueError, e:
            logger.warn('create player failed of invalid args: %r', e)
            return False
        return True

    def remove(self, name):
        player = self.players[name] if self.players.has_key(name) else None
        if not player: return False
        self.players.pop(name)
        player.stop()
        self.confs = filter(lambda c: c['name'] != name, self.confs)
        return True

    def stats(self):
        return map(lambda (_, p): p.stats(), self.players.items())

    def wait(self):
        while True:
            try:
                self._joinall()
            except (KeyboardInterrupt, SystemExit):
                self.stop()
                return

    def _joinall(self):
        for (_, player) in self.players.items():
            player.join(0.01)

    def _create(self, args, conf):
        players = {}
        for arg in args:
            player = self._create_one(arg, conf)
            players[player.name] = player
        return players

    def _create_one(self, arg, conf):
        conn_p, conn_c = Pipe()
        player = PlayerProcess(conn_p, conn_c, arg, conf)
        return player

class MultiPlayerPersist(MultiPlayer):
    PFILE = 'qplayer.json'

    def __init__(self, app_args, conf):
        try:
            js = common.read_file_json(self.PFILE)            
            logger.info('init player from persist file')              
            MultiPlayer.__init__(self, js, conf)
        except RuntimeError, e:
            logger.info('init player from confs')              
            MultiPlayer.__init__(self, app_args, conf) 
            self._persist()

    def append(self, arg):
        r = MultiPlayer.append(self, arg)
        if r: self._persist()
        return r

    def remove(self, name):
        r = MultiPlayer.remove(self, name)
        if r: self._persist()
        return r

    def _persist(self):
        common.write_file_json(self.PFILE, self.confs)

if __name__ == '__main__':
    pass

