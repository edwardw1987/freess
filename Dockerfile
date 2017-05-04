FROM ubuntu:latest
WORKDIR /root
RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/mirrors.163.com\/ubuntu\//g' /etc/apt/sources.list
COPY app /root/app
RUN apt-get clean && apt-get update
RUN apt-get install -y python-pip --fix-missing
RUN apt-get install -y libzbar0 libzbar-dev
COPY requirement.txt /root/requirement.txt
RUN pip install -r requirement.txt
EXPOSE 8000 1987 1988
ENTRYPOINT ["python", "/root/app/main.py"]

