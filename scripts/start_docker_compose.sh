#! /bin/bash

set -e
echo $PATH
# DOCKERPATH=$(whereis docker-compose) 
# echo $DOCKERPATH
PATH=$PATH:/usr/local/bin
echo $PATH
cd /usr/src/app &&
docker-compose up --build -d 