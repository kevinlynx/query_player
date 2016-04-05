# kevinlynx@gmail.com
import subprocess, os, sys
import urllib2, urllib, httplib, socket
import json

LIB_PATH = os.path.split(os.path.realpath(__file__))[0]
ROOT_PATH = os.path.join(LIB_PATH, "..")

def get_rel_path(p):
    return os.path.join(ROOT_PATH, p)

def run_cmd(cmd, nonblock = False):
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if nonblock: return
    out, err = p.communicate() 
    append_file('cmd.log', cmd + '\n')
    append_file('stdout.log', out)
    append_file('stderr.log', out)
    if p.returncode: 
        return p.returncode, err
    else: 
        return p.returncode, out

def remove_file(file):
    try: 
        os.remove(file)
    except:
        pass

def append_file(file, obj):
    with open(file, 'a') as fp:
        fp.write(obj)

def write_file(file, obj):
    with open(file, 'w') as fp:
        fp.write(obj)

def read_file_string(file):
    try:
        with open(file, 'r') as fp:
            s = fp.read()
            return s
    except IOError, e:
        return ''

def read_file_json(file):
    s = read_file_string(file)
    if s == '': raise RuntimeError(file + 'file empty')
    return json.loads(s)

def write_file_json(file, js):
    write_file(file, json.dumps(js, indent = 4))

def confirm_input(text = 'continue (y/n):'):
    sys.stdout.write(text)
    str = sys.stdin.readline().strip()
    return str == 'y'

def http_get(url, timeout = 1000, d_params = {}):
    return http_req(url, timeout, d_params)

def http_post(url, timeout = 1000, body = None, d_params = {}, headers = {}):
    return http_req(url, timeout, d_params, body, headers)

def http_req(url, timeout, d_params = {}, body = None, headers = {}):
    if len(d_params) > 0:
        q = urllib.urlencode(d_params)
        url = url + '?' + q
    content = ''
    try:
        request = urllib2.Request(url, body, headers)
        response = urllib2.urlopen(request, timeout = timeout)
        content = response.read() 
    except urllib2.HTTPError, e:
        pass
    except urllib2.URLError, e:
        print('request %s failed: %r' % (url, e))
    except socket.timeout, e:
        print('request %s failed, socket timeout %r' % (url, e))
    return content

if __name__ == '__main__':
    pass

