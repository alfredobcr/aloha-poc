#!/bin/bash

nohup python -m logunit.main > nohup.out 2>&1 &
echo $! > logunit.pid
nohup python -m dropunit.main > nohup.out 2>&1 &
echo $! > dropunit.pid
nohup python -m reducerunit.main > nohup.out 2>&1 &
echo $! > reducerunit.pid
nohup python -m starunit.main > nohup.out 2>&1 &
echo $! > starunit.pid

sleep 1

tail -f unit.log