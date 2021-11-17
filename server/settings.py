import os

class settings:
    disable_interactve_docs = os.getenv("DISABLE_INTERACTIVE_DOCS", False)
    domain_name = os.getenv("FRONTEND_DOMAIN_NAME", None)
    max_upload_size = os.getenv("MAX_UPLOAD_SIZE", 1_000_000_000)
    
    redis_host = os.getenv("REDIS_HOSTNAME", 'localhost')
    redis_port = os.getenv("REDIS_PORT", '6379')
    redis_db = os.getenv("REDIS_DB", '0')
    redis_password = os.getenv("REDIS_PASSWORD", None)
    if redis_password is not None:
        redis_url = f'redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}'
    else:
        redis_url = f'redis://{redis_host}:{redis_port}/{redis_db}'
        
    database_host = os.getenv('DATABASE_HOST', None)
    database_username = os.getenv('DATABASE_USERNAME', None)
    database_password = os.getenv('DATABASE_PASSWORD', None)
    database_name = os.getenv('DATABASE_NAME', None)
    if database_host is None:
        database_url = f"sqlite:///./{__name__.split('.')[0]}/localdb.sqlite"
    else:
        database_url = 'postgresql://'
        if database_username is not None:
            database_url += database_username
            if database_password is not None:
                database_url += f':{database_password}'
            database_url += '@'
        database_url += database_host
        if database_name is not None:
            database_url += f'/{database_name}'
