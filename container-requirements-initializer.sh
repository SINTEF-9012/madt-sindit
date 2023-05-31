#!/bin/bash

# Exit with an error if any command fails
set -e

apt-get update

apt-get install -y curl wget



# git required for the pke keyphrase extraction library (git pip link)
apt-get install -y git

pip install --no-cache-dir -r requirements.txt

# libgl required for CAD module
apt-get install -y libgl1

# required for textract (PDF text extraction) (but removed pstotext because it is no longer available!)
apt-get install -y python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig

# gcc required for tsfresh (timeseries feature extractor)
# tsfresh installation only works with the dependency (unlike the ones for other packages)
# apt-get install -y gcc
# pip install tsfresh

# Influx cli for remote backup / restore
wget https://dl.influxdata.com/influxdb/releases/influxdb2-client-2.4.0-amd64.deb
apt install ./influxdb2-client-2.4.0-amd64.deb
rm influxdb2-client-2.4.0-amd64.deb

# Inter-process communication
apt-get install -y memcached

apt-get clean

# Requirements for the pke keyphrase extraction library
# python -m spacy download en_core_web_sm

# OpenMMLab (must be after the pip requirements for mim)
# RUN mim install mmcv-full

# pip install torch==1.12.1+cpu torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
# pip install mmcv-full -f https://download.openmmlab.com/mmcv/dist/cpu/torch1.12.0/index.html

# RUN pip install mmdet
# cd dependencies

# git clone --depth=1 https://github.com/open-mmlab/mmdetection.git --branch v2.26.0

# cd mmdetection
# pip install -v -e .

# Install the model:
# mkdir checkpoints
# cd checkpoints
# mkdir faster_rcnn
# cd faster_rcnn
# wget https://download.openmmlab.com/mmdetection/v2.0/faster_rcnn/faster_rcnn_r50_fpn_1x_coco/faster_rcnn_r50_fpn_1x_coco_20200130-047c8118.pth

cd ../..