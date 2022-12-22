# redis docker build: https://www.runoob.com/docker/docker-install-redis.html
import redis
import json
import os

def createRedisClient(host, port):
    try:
        redisClient = redis.Redis(host=host, port=port)
        pingTest = redisClient.ping()

        if (pingTest == True):
            print("Connected To Redis!")
            return redisClient
        else:
            print("Could not connect to Redis!")
    except Exception as ex:
        print("Could not connect to redis! See Message Below")
        print(ex)
    return False

# cache flow:
# try to get redis cache data
# acquire a lock for data
# try again to get redis cache data
# if not found, use DB
# release lock

# cache flow is used to prevent simultaneously acquire a data

# get cache by transform string back to object


def getRedisValueByKey(key: str):
    output = redisClient.get(key)
    if output == None:
        with redisClient.lock('lock_' + key):
            output = redisClient.get(key)

    if output != None:
        output = json.loads(output)

    return output

# cache object with jsonify string


def setRedisKeyAndValue(key: str, value):
    value = json.dumps(value)
    output = redisClient.set(key, value)
    redisClient.expire(key, 600) # set 10 min data expiration time
    return output

redisClient = createRedisClient('localhost', 6379) if os.getenv("FROM") == 'LOCAL' else createRedisClient('redis', 6379)
