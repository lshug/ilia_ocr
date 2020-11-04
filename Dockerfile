FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./server /app/app
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt
RUN apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config poppler-utils
