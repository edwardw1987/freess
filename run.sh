#!/bin/sh
IMAGE="edward/freess"
CONTAINER="freess"
DOCKER="/usr/local/bin/docker"
arg="-i -d --rm"
$DOCKER run $arg --name $CONTAINER -p 1987:1987 -p 1988:1988 -p 8001:8000 $IMAGE 
