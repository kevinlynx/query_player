#!/bin/env python
# kevinlynx@gmail.com
import os, sys

HOME_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(HOME_PATH, ".."))
sys.path.append(os.path.join(HOME_PATH, "../lib"))

from player_process import MultiPlayer
import config

def main():
    player = MultiPlayer(config.APP, config.CONF)
    player.start()
    player.wait()

if __name__ == '__main__':
    main()

