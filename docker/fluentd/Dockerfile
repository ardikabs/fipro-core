FROM fluent/fluentd:v0.12
LABEL maintainer="Ardika" Description="Fluentd With Mongo Plugin" Version="0.1"

USER root
RUN apk add --update --virtual .build-deps \
        sudo build-base ruby-dev \
    && sudo gem install fluent-plugin-mongo \
    && sudo gem install fluent-plugin-record-modifier \
    && sudo gem install fluent-plugin-mqtt-io \
    && sudo gem sources --clear-all \
    && apk del .build-deps \
    && rm -rf  /var/cache/apk/* \
                /tmp/* /var/tmp/* \
                /home/fluent/.gem/ruby/2.3.0/cache/*.gem \
                /usr/lib/ruby/gems/*/cache/*.gems