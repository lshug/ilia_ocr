FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./server /app/app
COPY ./model_training/model.h5 /app/app/model.h5

# Install tesseract

RUN apt-get update
RUN apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev pkg-config

# Install conda

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

# Install conda packages

RUN conda install -c conda-forge numpy=1.19
RUN conda install -c anaconda scipy=1.5
RUN conda install -c conda-forge poppler=20.11
RUN conda install -c anaconda tensorflow-gpu=2.2.0

# Install pip packages

RUN pip3 install pydantic==1.7.2 fastapi==0.61.1 pdf2image==1.14.0 tesserocr==2.5.1 starlette==0.13.6 uvicorn==0.12.2 numpy==1.19.3 scipy==1.4.1 beautifulsoup4==4.9.3 Pillow==8.0.1 python-multipart==0.0.5 aiofiles==0.6.0




