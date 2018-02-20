#!/bin/sh
IMAGE="edward/freess"
DOCKER=$(which docker);
COMPOSE=$(which docker-compose);
NAME="freess"

if [ -n "$($DOCKER ps|grep $IMAGE)" ]; then
  echo "removing...";
  $DOCKER rm -vf $NAME;
fi
arg="-d"

$COMPOSE up $arg $NAME;
