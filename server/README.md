# FastAPI server


## main.py

FastAPI microservice. Pass static file directory with OCR_STATIC_FILES_DIRECTORY environment variable. For interactive documentation, run the server and go to http://localhost:8000/docs. For CORS, pass the front-end domain name with FRONTEND_DOMAIN_NAME environment variable. Default maximum upload size is 500000000, and can be changed by setting MAXIMUM_UPLOAD_SIZE environmental variable.

## dataprocessor.py

Data loading and preprocessing logic.

## model_serving.py

Model serving.

## utis.py

Utilities for erosion.

## middleware.py
Server middleware.

## launch.sh

Script for launchng the microservice.
