#!/bin/env python
# kevinlynx@gmail.com
import select, socket, sys, thread
from threading import Thread

class ProxyLite(Thread):
    BUFFERSIZE = 2 ** 12

    def __init__(self, local, remote):
        Thread.__init__(self)
        self.local = local
        self.remote = remote
        self.is_stop = False

    def start(self):
        Thread.start(self)

    def stop(self):
        self.is_stop = True
        try:
            dummy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dummy.connect(self.local)
            dummy.shutdown(socket.SHUT_RDWR)
            dummy.close()
        except:
            pass
        self.join(0.01) 

    def run(self):
        proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        proxy.bind(self.local)
        proxy.listen(10)
        while not self.is_stop:
            client = proxy.accept()[0]
            if self.is_stop: 
                client.close()
                break
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.connect(self.remote)
            thread.start_new_thread(self._serve, (client, server))
        proxy.shutdown(socket.SHUT_RDWR)
        proxy.close()

    def _serve(self, client, server):
        pairs = {client: server, server: client}
        while pairs:
            read, write, error = select.select(pairs.keys(), [], [])
            for sock in read:
                string = sock.recv(self.BUFFERSIZE)
                if string:
                    pairs[sock].sendall(string)
                else:
                    self._safe_shut(pairs[sock], socket.SHUT_WR)
                    self._safe_shut(sock, socket.SHUT_RD)
                    del pairs[sock]
        client.close()
        server.close()

    def _safe_shut(self, sock, type):
        try:
            sock.shutdown(type)
        except:
            pass

def main(local, remote):
    proxy = ProxyLite(local, remote)
    proxy.start()
    while True:
        try:
            proxy.join(0.01)
        except (KeyboardInterrupt, SystemExit):
            proxy.stop()
            break

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s proxy:port server:port' % sys.argv[0])
        sys.exit(0)
    def parse_spec(s):
        vec = s.split(':')
        return vec[0], int(vec[1])
    main(parse_spec(sys.argv[1]), parse_spec(sys.argv[2]))

