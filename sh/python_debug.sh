#!/bin/bash
{ opkitctl && nc --version; } > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: please install opkitctl and ncat first"
fi

if [ $# -ne 1 ]; then
    echo "Error: need to specify PID"
    exit 1
fi

PID=$1
SOCK_FILE="/tmp/rpdb_${PID}"

rm -f $SOCK_FILE

if [ -n "${PID}" ];then
    echo "Injecting process ${PID}..."
    (opkitctl trace "${PID}" ori >/dev/null 2>&1)&
fi

echo "Connecting to ${SOCK_FILE}..."
sleep 2 && nc -U $SOCK_FILE
exit $?
