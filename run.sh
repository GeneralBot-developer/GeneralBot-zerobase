#!/bin/bash
cmd="sudo docker-compose -f docker-compose.$1.yml -p $1 ${@:2}"
set -eu
echo $cmd
eval $cmd