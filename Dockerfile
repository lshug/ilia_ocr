FROM lshug/uvicorn-gunicorn-fastapi-tesserocr-tensorflow:python3.8

#Copy server files
COPY ./server /app/app

# wget model.h5
RUN wget -O /app/app/model.h5 https://github.com/lshug/ilia_ocr/raw/main/model_training/model.h5
