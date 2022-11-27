#! /bin/bash

set -e
PATH=$PATH:/usr/local/bin
(cd /usr/src/app && docker-compose down) || echo "do nothing"