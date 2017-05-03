#!/bin/sh
IMAGE="edward/freess"
DOCKER="/usr/local/bin/docker"
arg="-i $1"
$DOCKER run $arg -p 1987:1987 -p 1988:1988 -p 8001:8000 $IMAGE
