FROM python:3.8

#Set up miniconda

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 libgl1-mesa-glx ca-certificates curl git python3-lxml && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    /opt/conda/bin/conda clean -tipsy && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc



# tesserocr, bs4 for parsing hocr
RUN conda install -c conda-forge tesserocr=2.5.1
RUN conda install -c conda-forge beautifulsoup4=4.9.3

# stuff for cv and inference
RUN conda install -c conda-forge scipy=1.5.3
    
# server stuff
RUN conda install -c anaconda redis=5.0.3
RUN python3 -m pip install --no-cache-dir uvicorn==0.12.2 gunicorn==20.0.4 fastapi==0.61 pydantic==1.7.2 uvloop==0.14.0 websockets==8.1 httptools==0.1.1 python-multipart==0.0.5 aiofiles==0.6.0 sqlalchemy==1.3 SQLAlchemy-Utils==0.37.9 databases[sqlite,postgresql]==0.4.1 psutil==5.7.3 alembic==1.4.3 redis==3.5.3 celery[redis]==5.0.2 psycopg2==2.9.2 lxml==4.6.4
COPY ./resources/start.sh /start.sh
COPY ./resources/ge.traineddata /opt/conda/share/tessdata/ge.traineddata
RUN chmod +x /start.sh
COPY ./resources/gunicorn_conf.py /gunicorn_conf.py
COPY ./resources/start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh
RUN mkdir /app/
WORKDIR /app/
ENV PYTHONPATH=/app
EXPOSE 80
CMD ["/start.sh"]

COPY ./server /app/app
