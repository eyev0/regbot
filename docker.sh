#!/bin/sh
#echo docker rm -f $2
#docker rm -f $2
#echo docker cp app:/usr/src/app/data/f ~/dev/py/app/data/container/

#echo docker build --tag $1:latest .
#docker build --tag $1:latest .
#
#echo docker rm -f $1
#docker rm -f $1
#
#echo docker container run -it -d --name $1 $1
#docker container run -it -d --name $1 $1
#echo done!

echo
echo "docker build -t $1:latest ."
echo
docker build -t "$1":latest .

old_name=$(docker ps --filter "name=$1" --filter status=running --format="{{.Names}}")
new_name=$(docker ps --filter "name=$1" --filter status=running --format='{{.Names}}')-$(date +'%F-%H-%M-%S')

echo
echo "docker rename $old_name $new_name"
echo
docker rename "$old_name" "$new_name"

if [ "$2" == "stop" ]; then
  echo
  echo "docker stop $new_name"
  echo
  docker stop "$new_name"
fi

echo
echo "docker container run -d -it -v ~/db/$1:/db -v ~/logs/$1:/log --name $1 $1"
echo
docker container run -d -it -v ~/db/"$1":/db -v ~/logs/"$1":/log --name "$1" "$1"