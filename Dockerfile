# Dockerfile exported by GearBuilderGUI. Stash edits before export again

# Inheriting from established docker image:
FROM ubuntu:xenial

# Inheriting from established docker image:
LABEL maintainer="Flywheel <support@flywheel.io>"

# Install APT dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tcsh \
    tar \
    wget \
    libgomp1 \
    perl-modules \
    bc \
    python3-pip  \
    git \ 
    zip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev && \ 
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#############################################
# Download and install FreeSurfer and make minimal (2.9 GB)
# 6.0.1 ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.1/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.1.tar.gz
# 5.3.0 ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/5.3.0-HCP/freesurfer-Linux-centos4_x86_64-stable-pub-v5.3.0-HCP.tar.gz
RUN wget -nv -O- ftp://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.1/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.1.tar.gz | tar zxv -C /opt \
    --exclude='freesurfer/trctrain' \
    --exclude='freesurfer/subjects/fsaverage_sym' \
    --exclude='freesurfer/subjects/fsaverage3' \
    --exclude='freesurfer/subjects/fsaverage4' \
    --exclude='freesurfer/subjects/fsaverage5' \
    --exclude='freesurfer/subjects/fsaverage6' \
    --exclude='freesurfer/subjects/cvs_avg35' \
    --exclude='freesurfer/subjects/cvs_avg35_inMNI152' \
    --exclude='freesurfer/subjects/bert' \
    --exclude='freesurfer/subjects/V1_average' \
    --exclude='freesurfer/average/mult-comp-cor' \
    --exclude='freesurfer/lib/cuda' \
    --exclude='freesurfer/lib/qt'  && \
    rm -rf /opt/freesurfer/subjects/* && \
    rm -rf /opt/freesurfer/average/* && \
    rm -rf /opt/freesurfer/mni/* && \
    mkdir /stash && \
    mv /opt/freesurfer/bin/* /stash/ && \
    cp /stash/mri_conv* /opt/freesurfer/bin/ && \
    rm -rf /stash

# Set up the FreeSurfer environment
ENV OS=Linux \ 
    FS_OVERRIDE=0 \ 
    FIX_VERTEX_AREA= \ 
    SUBJECTS_DIR=/opt/freesurfer/subjects \ 
    FSF_OUTPUT_FORMAT=nii.gz \ 
    MNI_DIR=/opt/freesurfer/mni \ 
    LOCAL_DIR=/opt/freesurfer/local \ 
    FREESURFER_HOME=/opt/freesurfer \ 
    FSFAST_HOME=/opt/freesurfer/fsfast \ 
    MINC_BIN_DIR=/opt/freesurfer/mni/bin \ 
    MINC_LIB_DIR=/opt/freesurfer/mni/lib \ 
    MNI_DATAPATH=/opt/freesurfer/mni/data \ 
    FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast \ 
    PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5 \ 
    MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5 \ 
    PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

# Install PIP Dependencies
RUN pip3 install --upgrade pip && \ 
    pip3.5 install \
    flywheel-sdk  \ 
    nibabel \
    setuptools && \
    pip3.5 install \
    psutil && \ 
    rm -rf /root/.cache/pip

RUN cd /opt/ && \
    git clone https://github.com/ai-med/quickNAT_pytorch.git && \
    cd /opt/quickNAT_pytorch && \
    pip install -r requirements.txt && \
    rm -rf .git
    

# copy patch to ensure CPU compatibility
COPY patch/evaluator.py /opt/quickNAT_pytorch/utils/
COPY settings_eval.ini /opt/quickNAT_pytorch/
COPY test_list.txt /opt/quickNAT_pytorch/

# Specify ENV Variables
ENV \ 
    PATH=$PATH  \ 
    LD_LIBRARY_PATH=$LD_LIBRARY_PATH \
    PYTHONPATH=/opt/quickNAT_pytorch/ 

# Make directory for flywheel spec (v0):
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

RUN ln -s /opt/quickNAT_pytorch/run.py /flywheel/v0/quickNAT.py
# Copy executable/manifest to Gear
COPY run.py ${FLYWHEEL}/run.py
COPY util ${FLYWHEEL}/util
COPY manifest.json ${FLYWHEEL}/manifest.json

# ENV preservation for Flywheel Engine
RUN python3 -c 'import os, json; f = open("/tmp/gear_environ.json", "w");json.dump(dict(os.environ), f)'

ENTRYPOINT ["/flywheel/v0/run.py"]
# Configure entrypoint