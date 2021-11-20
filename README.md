# ilia_ocr
The recommended method for running the server is to build and run the docker image. 

```
docker build -t ilia_ocr github.com/lshug/ilia_ocr
docker run -p 127.0.0.1:8000:80 ilia_ocr
```

Alternatively, if all dependencies are installed, you can test the server with:

```
python3 -m uvicorn server.main:app
```

Dependencies can be installed using the provided conda environment (environment.env). However, the following packages should be available system-wide:

```wget bzip2 libgl1-mesa-glx ca-certificates curl git```

Swagger UI can be accessed from /docs endpoint.

## Environment variables
  * *DISABLE_INTERACTIVE_DOCS*: set to any value to disable interactive docs
  * *FRONTEND_DOMAIN_NAME*: front-end domain name on which to enable CORS
  * *MAXIMUM_UPLOAD_SIZE*: overrides maximum upload size of 1000000000 bytes
  * *REDIS_HOSTNAME*: redis hostname. Will use local instance if not set.
  * *REDIS_PORT*: redis port. Default: 6379.
  * *REDIS_DB*: Default: 0.
  * *REDIS_PASSWORD*: redis password. Default: None.
  * *DATABASE_HOST*: PostgreSQL hostname
  * *DATABASE_USERNAME*: PostgreSQL username
  * *DATABASE_PASSWORD*: PostgreSQL password
  * *DATABASE_NAME*: PostgreSQL database name
  * Env vars described [here](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#environment-variables)
  
