#!/bin/sh
echo
echo "docker build -t $1:$2 ."
echo
docker build -t "$1":"$2" .

echo
echo "docker kill --signal=SIGINT $1"
echo
docker kill --signal=SIGINT "$1"

echo
echo "sleep 2"
echo
sleep 2

echo
echo "docker container prune --force"
echo
docker container prune --force

echo
echo "docker container run -d -it -v ~/$1:/vol --name $1 $1:$2"
echo
docker container run -d -it -v ~/"$1":/vol --name "$1" "$1:$2"