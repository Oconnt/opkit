#!/bin/bash

# 函数：获取系统资源使用情况
get_system_usage() {
    echo "系统CPU使用率:"
    mpstat | tail -1 | awk '{print 100 - $12"%"}'
    echo "系统内存使用率:"
    free | awk '/Mem/{printf("%.2f%\n", $3/$2*100)}'
    echo "系统磁盘使用率:"
    df -h
}

# 函数：获取特定进程资源使用情况
get_process_usage() {
    local pid=$1
    if ps -p $pid > /dev/null; then
        echo "进程 $pid 的CPU使用率:"
        ps -p $pid -o %cpu=
        echo "进程 $pid 的内存使用率:"
        ps -p $pid -o %mem=
        echo "进程 $pid 的磁盘使用率:"
        lsof -p $pid | awk '{sum+=$9} END {print sum}'
    else
        echo "进程 $pid 不存在"
    fi
}

# 主逻辑
if [ $# -eq 0 ]; then
    get_system_usage
else
    get_process_usage $1
fi
