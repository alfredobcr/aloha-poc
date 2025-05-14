#!/bin/bash
for unit in *.pid; do kill -9 `cat $unit`; rm $unit; done
rm unit.log
rm nohup.out