#!/bin/env python
# kevinlynx@gmail.com
import os, sys, json, datetime

HOME_PATH = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(os.path.join(HOME_PATH, ".."))
sys.path.append(os.path.join(HOME_PATH, "../lib"))

from lib.log import logger
from lib.player_process import MultiPlayerPersist
import config

from gevent import monkey; monkey.patch_all(thread = False, socket = False)
from gevent.pywsgi import WSGIServer
import flask
from flask import Flask, request, Response, make_response
from flask import render_template, redirect, url_for, jsonify

app = Flask(__name__, static_url_path = '/static')
app.debug = True
player = MultiPlayerPersist(config.APP, config.CONF)

@app.template_filter('dateformat')
def format_timestamp(t):
    if t == 0: return ''
    return datetime.datetime.fromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    confs = player.confs
    stats = player.stats()
    stat_confs = merge_stats_conf(confs, stats)
    return render_template('main.html', stat_confs = stat_confs)

def merge_stats_conf(confs, stats):
    def find_conf(n): return next(c for c in confs if c['name'] == n)
    def merge(s): 
        s['conf'] = find_conf(s['name'])
        return s
    return map(lambda s: merge(s), stats)

@app.route('/api/stats')
def get_stats():
    stats = player.stats()
    return Response(json.dumps(stats), mimetype='application/json')

@app.route('/api/conf_stats')
def get_conf_stats():
    confs = player.confs
    stats = player.stats()
    stat_confs = merge_stats_conf(confs, stats)
    return Response(json.dumps(stat_confs), mimetype='application/json')

@app.route('/api/add', methods = ['POST'])
def add_player():
    args = json.loads(request.data)
    if not args or not args.has_key('name'): return json_result(False)
    ret = player.append(args)
    return json_result(ret)

@app.route('/api/remove/<name>')
def remove_player(name):
    ret = player.remove(name)
    return json_result(ret)

def json_result(ret, msg = ''):
    js = {'success': ret, 'msg': msg}
    return Response(json.dumps(js), mimetype='application/json')

def main(port):
    player.start()
    try:
        WSGIServer(('', port), app).serve_forever()
    except (KeyboardInterrupt, SystemExit):
        print('exit')
    player.stop()

def main_view():
    app.run(host = '0.0.0.0', port = 7001)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = 7000
    main(port)

