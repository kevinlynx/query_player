# kevinlynx@gmail.com
import time
from log import logger

__all__ = ['Query', 'parse']

class Query:
    def __init__(self, tm, qs):
        self.tm = tm
        self.query = qs

def parse(parse_fn, line):
    try:
        return _do_parse(parse_fn, line)
    except Exception, e:
        logger.warn('parse query failed: %r [%s]', e, line)
    return None

def _do_parse(parse_fn, line):
    secs = line.split()
    if len(secs) < 2:  # at least date-time & query string
        logger.warn('invalid log: %s', line)
        return None
    parse_fn = parse_fn or _default_parse
    tm, qs = parse_fn(line)
    if tm == 0: return None
    return Query(tm, qs)

def _default_parse(line):
    secs = line.split()
    tm = _parse_time(secs[0] + ' ' + secs[1])
    query = secs[-1]
    return tm, query

def _parse_time(s):
    ms = int(s[s.index('.') + 1 :])
    dt = time.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
    return int(time.mktime(dt) * 1000 + ms)

