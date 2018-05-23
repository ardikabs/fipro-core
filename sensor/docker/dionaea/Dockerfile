FROM debian:stretch-slim
ENV DEBIAN_FRONTEND noninteractive

# Include dist and build script
ADD dist/ /root/dist/
COPY build.sh /root/

# Install dependencies, packages and dionaea
RUN /bin/bash /root/build.sh && \
    addgroup --gid 3500 dionaea && \
    adduser --system --no-create-home --shell /bin/bash --uid 3500 --disabled-password --disabled-login --gid 3500 dionaea && \
    chown -R dionaea:dionaea /opt/dionaea/var && \
    rm -rf /opt/dionaea/etc/dionaea/* && \
    mv /root/dist/etc/* /opt/dionaea/etc/dionaea/ && \
    mv /root/dist/supervisor/*.conf /etc/supervisor/conf.d/ && \
    rm -rf /root/* /var/lib/apt/lists/* /var/tmp/*

# Start dionaea
CMD ["/usr/bin/supervisord", "--nodaemon", "-c", "/etc/supervisor/supervisord.conf"]