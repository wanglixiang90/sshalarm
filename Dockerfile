FROM python:2.7.16-alpine
MAINTAINER Wanglx <15201376500@163.com>

WORKDIR /app
COPY . /app

RUN set -ex \
	&& apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
	&& echo "Asia/Shanghai" > /etc/timezone && apk del tzdata \
	&& pip install -r requirements.txt \
	&& rm -rf ~/.cache/pip && chmod 755 run.sh

EXPOSE 9090
ENTRYPOINT ["./run.sh"]

