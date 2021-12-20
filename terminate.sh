#!/usr/bin/env bash

for pid in $(pidof nfcbot_51d66f7d)
do
  echo "terminating $pid"
  kill -s TERM "$pid"
done