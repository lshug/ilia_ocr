# ilia_ocr
Repository for the OCR team. The recommended method for running the server is to build and run the docker image. Alternatively, if all dependencies are installed, you can test the server with:

```
uvicorn server.main:app
```

Swagger UI can be accessed from /docs endpoint.

## Environment variables
  * *DISABLE_INTERACTIVE_DOCS*: set to any value to disable interactive docs
  * *FRONTEND_DOMAIN_NAME*: front-end domain name on which to enable CORS
  * *MAXIMUM_UPLOAD_SIZE*: overrides maximum upload size of 1000000000 bytes
  * *REDIS_HOSTNAME*: redis hostname. Will use local instance if not set.
  * *REDIS_PORT*: redis port. Default: 6379.
  * *REDIS_DB*: Default: 0.
  * *REDIS_PASSWORD*: redis password. Default: None.
  * *DATABASE_URL*: PostgreSQL connection string. Will use a local sqlite if not provided.
  * Env vars described [here](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#environment-variables)
  
