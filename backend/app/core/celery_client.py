from celery import Celery
from ..config import REDIS_URL

app = Celery(
    "worker", 
    broker=REDIS_URL,
)