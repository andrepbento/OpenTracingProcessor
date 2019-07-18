# Author: André Bento
FROM alpine:3.9
MAINTAINER apbento "apbento@student.dei.uc.pt"

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

COPY . /Graphy
WORKDIR /Graphy

RUN pip3 install -r requirements.txt

#CMD ["python3", "setup.py", "run"]