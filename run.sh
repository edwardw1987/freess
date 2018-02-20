#!/bin/sh
IMAGE="edward/freess"
DOCKER=$(which docker);
NAME="freess"

if [ -n "$($DOCKER ps|grep $IMAGE)" ]; then
  echo "removing...";
  $DOCKER rm -vf $NAME;
fi
arg="-d"
cmd="$DOCKER run $arg \
--name $NAME \
-p 1987:1987 \
-p 1988:1988 \
-p 8008:8008 
--restart=unless-stopped \
$IMAGE"
echo $cmd;
$cmd;
