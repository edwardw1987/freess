FROM ubuntu:latest
WORKDIR /root
COPY app /root/app
RUN apt-get update

RUN apt-get install -y python-pip
RUN apt-get install -y libzbar0 libzbar-dev
RUN apt-get install --fix-missing
COPY requirement.txt /root/requirement.txt
RUN pip install -r requirement.txt
EXPOSE 8000 1987 1988
ENTRYPOINT ["python", "/root/app/main.py"]

