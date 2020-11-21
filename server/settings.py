import os

class settings:
    disable_interactve_docs = os.getenv("DISABLE_INTERACTIVE_DOCS", None)
    domain_name = os.getenv("FRONTEND_DOMAIN_NAME", None)
    files_path = os.getenv("OCR_STATIC_FILES_DIRECTORY", f"{os.path.dirname(__file__)}/files/")

    redis_host = os.getenv("REDIS_HOSTNAME", 'localhost')
    redis_port = os.getenv("REDIS_PORT", '6379')
    redis_db = os.getenv("REDIS_DB", '0')
    redis_password = os.getenv("REDIS_PASSWORD", None)
    if redis_password is not None:
        redis_url = f'redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}'
    else:
        redis_url = f'redis://{redis_host}:{redis_port}/{redis_db}'

# postgresql connect string
# max GPUs
