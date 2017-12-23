FROM phusion/baseimage:0.9.18

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y --force-yes install python3 python3-pip && \
    pip3 install --upgrade six && \
    pip3 install django==1.8.18 werkzeug gunicorn python-dateutil cinp

COPY architect /usr/lib/python3/dist-packages/architect
COPY local /usr/local/architect
COPY docker/etc/ /etc/

EXPOSE 8880

CMD [ "/sbin/my_init" ]
