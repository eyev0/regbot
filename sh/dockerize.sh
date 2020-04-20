#!/bin/sh
#echo docker rm -f $2
#docker rm -f $2
#echo docker cp regbot:/usr/src/app/data/f ~/dev/py/regbot/data/container/
echo docker build --tag $1:latest .
docker build --tag $1:latest .

echo docker rm -f $1
docker rm -f $1

echo docker container run -it -d --name $1 $1
docker container run -it -d --name $1 $1
echo done!