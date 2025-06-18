import redis
from decouple import config
r = redis.Redis.from_url(config("REDIS_URL"), decode_responses=False)
