FROM fluent/fluentd:v0.12
LABEL maintainer="Ardika" Description="Fluentd With Custom Plugin" Version="1.1"

USER root
RUN apk add --update --virtual .build-deps sudo build-base ruby-dev automake autoconf libtool libc6-compat \
    && apk add --no-cache geoip geoip-dev libmaxminddb \
    && sudo gem install fluent-plugin-mongo \
    && sudo gem install fluent-plugin-record-modifier \
    && sudo gem install fluent-plugin-geoip \
    && sudo gem install fluent-plugin-mqtt-io \
    && sudo gem sources --clear-all \
    && apk del .build-deps \
    && rm -rf  /var/cache/apk/* \
    && rm -rf /tmp/* /var/tmp/* \
    && rm -rf /home/fluent/.gem/ruby/2.3.0/cache/*.gem \
    && rm -rf /usr/lib/ruby/gems/*/cache/*.gems