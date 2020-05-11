#!/bin/sh
echo
echo "docker kill --signal=SIGINT $1"
echo
docker kill --signal=SIGINT "$1"

echo
echo "docker start $1"
echo

docker start "$1"