FROM ubuntu:16.04

MAINTAINER Amazon SageMaker Examples <vivek.kushwaha@tcs.com>

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    wget \
    r-base \
    r-base-dev \
    ca-certificates

RUN R -e "install.packages(c('mda', 'plumber'), repos='https://cloud.r-project.org')"

COPY serve.R /opt/ml/serve.R
COPY plumber.R /opt/ml/plumber.R

ENTRYPOINT ["/usr/bin/Rscript", "/opt/ml/serve.R", "--no-save"]
