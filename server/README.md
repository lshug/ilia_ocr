# FastAPI server


## main.py

FastAPI microservice. Pass static file directory with OCR_STATIC_FILES_DIRECTORY environment variable. For interactive documentation, run the server and go to http://localhost:8000/docs (can be disabled by setting DISABLE_INTERACTIVE_DOCS environment variable). For CORS, pass the front-end domain name with FRONTEND_DOMAIN_NAME environment variable. Default maximum upload size is 500000000, and can be changed by setting MAXIMUM_UPLOAD_SIZE environmental variable. 


### Environment variables:

  * *OCR_STATIC_FILES_DIRECTORY*: static file directory
  * *DISABLE_INTERACTIVE_DOCS*: set to any value to disable interactive docs
  * *FRONTEND_DOMAIN_NAME*: front-end domain name on which to enable CORS
  * *MAXIMUM_UPLOAD_SIZE*: overrides maximum upload size of 1000000000 bytes

  
## data_processor.py

Data loading and processing logic.

## model_serving.py

Model serving.

## utis.py

Data loading and processing utils (erosion).

## server_utils.py

Server utils.

## tests_main.py

Unit tests.

## launch.sh

Script for launchng the microservice.
