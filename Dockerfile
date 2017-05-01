FROM ubuntu:latest
WORKDIR /root
COPY app /root/app
COPY requirement.txt /root/requirement.txt
RUN apt-get update

RUN apt-get install -y python-pip
RUN pip install -U requrement.txt

