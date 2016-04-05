APP = [
{
    'name': 'player1',
    'host': '10.181.97.3:3388',
    'qsize': 1000,
    'loader': {
        'name': 'loader_star',
        'args': {
            'host': '127.0.0.1:8182',
            'file': '/home/admin/sp_mini/logs/access_log_sp',
            'taskid': 'qplayer-1'
        }
    }
},
{
    'name': 'player2',
    'host': '10.181.97.3:3388',
    'qsize': 1000,
    'loader': {
        'name': 'loader_star',
        'args': {
            'host': '127.0.0.1:8182',
            'file': '/home/admin/sp_mini/logs/access_log_sp',
            'taskid': 'qplayer-2'
        }
    }
}
]

CONF = {
    'loader': {
        # a function: tm, query_str = parse(line)
        'parse': None
    },
    'player': {
        'http_header': {
            'EagleEye-ClusterTest': 1
        },
        'timeout': 100,
        # in io task count; and wait io task count
        'wait_count': 10000,
        'conn_pool_size': 1000,
    }
}

