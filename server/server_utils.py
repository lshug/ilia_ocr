from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from celery import Celery
import redis
import string
import random
import subprocess
import os
import psutil
from .settings import settings

class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_size: int) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "POST":
            if "content-length" not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers["content-length"])
            if content_length > self.max_upload_size:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        return await call_next(request)

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str

def start_redis_celery():
    if settings.redis_host == 'localhost' and not any(['redis-server' in x for x in list((p.name() for p in psutil.process_iter()))]):
        subprocess.Popen('redis-server')
    if not any(['celery' in x for x in list((p.name() for p in psutil.process_iter()))]):
        env = os.environ.copy()
        subprocess.Popen(['celery', '-A', __name__.split('.')[0]+'.data_processor', 'worker','--loglevel=INFO'], env=env)


redis_session = redis.StrictRedis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db, password=settings.redis_password)
celery_app = Celery('data_processing', broker=settings.redis_url)
