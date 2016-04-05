## Query Player

A user-level query copy service like tcpcopy, but can be deployed/managed much more easily. Also less CPU sys cost.

## Feature

* copy http query (request) to remote server
* load http queries from custom loader (loader is an object to load http query), currently supported loaders:
    * local file, support file rotatating
    * staragent
* a simple http service to append/remove player at runtime; the service supports to running multiple players
* configurable query parser, http header

## Usage

Requirements:

* Python 2.7+
* gevent
* geventhttpclient
* flask (if use http service)

Recommend running by http service:

```
./service/app.py
```

Visit: `http://ip:7000` to append query player

## Config

see `config.py`
