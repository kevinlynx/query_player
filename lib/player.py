# kevinlynx@gmail.com
from play_task import PlayTask
from Queue import Queue
from query_loader import QueryLoader

class Player:
    def __init__(self, host, loader, load_conf, play_conf, qsize = 1000):
        self.queue = Queue(qsize)
        self.task = PlayTask(self.queue, host, play_conf)
        self.loader = QueryLoader(self.queue, loader, load_conf)

    def start(self):
        self.loader.start()
        self.task.start()

    def stop(self):
        self.task.stop() 
        self.loader.stop()

    def stats(self):
        return {'qsize': self.queue.qsize(), 
            'task': self.task.stats(), 'loader': self.loader.stats()}

    def wait(self):
        while True:
            try:
                self.loader.join(0.01)
            except (KeyboardInterrupt, SystemExit):
                self.stop()
                return

if __name__ == '__main__':
    pass
