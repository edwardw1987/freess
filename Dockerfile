FROM ubuntu:latest
WORKDIR /root/app
RUN sed -i 's/http:\/\/archive.ubuntu.com\/ubuntu\//http:\/\/mirrors.163.com\/ubuntu\//g' /etc/apt/sources.list
COPY app /root/app
COPY pip.conf /root/.pip/pip.conf
RUN apt-get clean && apt-get update
RUN apt-get install -y python-pip --fix-missing
RUN apt-get install -y libzbar0 libzbar-dev
RUN pip install -r requirement.txt
RUN apt-get install -y vim
EXPOSE 8008 1987 1988
ENTRYPOINT ["gunicorn", "-c", "/root/app/conf/gunicorn_conf_dev.py", "main:app"]

