#!/bin/sh

PID=`ps -ef | grep "python3 startServer.py" | grep -v "grep" | awk '{print $2}'`

if [ ! -z "$PID" ]; then
  for p in "$PID"
  do
    kill -9 $p
  done
fi

nohup python3 startServer.py&
