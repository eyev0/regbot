#!/bin/sh
echo
echo "docker build -t $1:$2 ."
echo
docker build -t "$1":"$2" .

old_name=$(docker ps --filter "name=$1" --filter status=running --format="{{.Names}}")
new_name=$(docker ps --filter "name=$1" --filter status=running --format='{{.Names}}')-$(date +'%F-%H-%M-%S')

echo
echo "docker rename $old_name $new_name"
echo
docker rename "$old_name" "$new_name"

echo
echo "docker kill --signal=SIGINT $new_name"
echo
docker kill --signal=SIGINT "$new_name"

echo
echo "docker container run -d -it -v ~/$1:/vol --name $1 $1:$2"
echo
docker container run -d -it -v ~/"$1":/vol --name "$1" "$1:$2"