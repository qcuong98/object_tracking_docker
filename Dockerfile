FROM nvidia/cuda:9.0-devel-ubuntu16.04
RUN apt-get update && apt-get install -y wget git

# Install Miniconda
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda create -n env python=3.6
RUN echo "source activate env" > ~/.bashrc

SHELL ["/bin/bash", "-c"]

# Install libraries
RUN source activate env && \
    conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
RUN source activate env && \
    conda config --add channels conda-forge
RUN source activate env && conda install -y \
    pytorch=0.4.1 torchvision cuda90 opencv cython numba \
    progress matplotlib easydict scipy tqdm
ARG PYTORCH=/root/miniconda3/envs/env/lib/python3.6/site-packages/
RUN sed -i "1254s/torch\.backends\.cudnn\.enabled/False/g" ${PYTORCH}/torch/nn/functional.py


COPY . /app

# Install COCOAPI
WORKDIR /app
ENV COCOAPI="cocoapi"
ARG COCOAPI="cocoapi"
RUN git clone --depth 1 https://github.com/cocodataset/cocoapi.git 'cocoapi'
WORKDIR /app/$COCOAPI/PythonAPI
RUN source activate env && make
RUN source activate env && python setup.py install --user

# Install Detector
WORKDIR /app/CenterNet/src/lib/external
RUN source activate env && python setup.py build_ext --inplace

# Install DCN2
# WORKDIR /app/CenterNet/src/lib/models/networks/DCNv2
# RUN source activate env && ./make.sh

WORKDIR /app/