FROM alpine:3.6
EXPOSE 8880
RUN apk add --no-cache python3 && pip3 install django==1.8.18 werkzeug gunicorn python-dateutil cinp
COPY architect /usr/lib/python3.6/site-packages/architect
COPY local /usr/local/architect
RUN mkdir -p /opt/architect && /usr/local/architect/util/manage.py migrate && /usr/local/architect/util/testData docker && /usr/local/architect/cron/planEvaluate
CMD /usr/local/architect/api_server/api_server.py
