#!/bin/sh
# kevinlynx@gmail.com
cmd=$1
port=$2
ref_file="/tmp/__star_proxy_ref_$port"
ref_cnt=0
base_home=`readlink -f "$(dirname "$0")"`
bin=$base_home/proxy_lite.py

if [ -f $ref_file ];then
    ref_cnt=`cat $ref_file`    
fi

start()
{
    if [ $ref_cnt -gt 0 ];then
        echo $(($ref_cnt + 1)) > $ref_file
        echo 'already started'
        exit 0
    fi
    echo 1 > $ref_file
    $bin 0.0.0.0:$port localhost:8182
}

stop()
{
    echo $(($ref_cnt - 1)) > $ref_file
    ref_cnt=`cat $ref_file`
    if [ $ref_cnt -gt 0 ];then
        exit 0
    fi
    kill -9 `ps aux | grep "$bin" | grep -v grep | awk '{print $2}'`
}

if [ "x$cmd" == "xstart" ];then
    start
elif [ "x$cmd" == "xstop" ];then
    stop
else
    echo 'invalid command'
fi

