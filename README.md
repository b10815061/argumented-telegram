current python version : python 3.9.7

# how to use

## build the application (used only if we have code or any concept changes)

```
$ cd <the/path/of/the/application>
(you should see docker-compose.yml here)
$ docker-compose up --build
```

please install and build redis first following the instructions here: https://www.runoob.com/docker/docker-install-redis.html

the build command takes longer to run, as it runs the all setup commands for docker, as well as compiles the main application.

## start the application (used if there's no need to change, adjust previous version of the application)

```
$ cd <the/path/of/the/application>
(you should see docker-compose.yml here)
$ docker-compose up
```

## stop the application

```
$ cd <the/path/of/the/application>
(you should see docker-compose.yml here)
$ docker-compose down
```

# issue tickets in docker-compose 

## user(role) "tommy" does not exists when connecting to postgres

-> try restart docker-compose

```
$ docker-compose down
$ docker-compose up
```

## module socketio does not have attribute AsyncServer

-> reinstall python-socketio

```
$ docker exec -it app bash
(in docker)
$ pip uninstall python-socketio -y
$ pip install python-socketio
```