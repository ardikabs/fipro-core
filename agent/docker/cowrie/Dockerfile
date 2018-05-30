FROM alpine
ENV DEBIAN_FRONTEND noninteractive

# Include dist and build script
ADD dist/ /root/dist/
COPY build.sh /root/

# Install dependencies, packages and cowrie
RUN chmod +x /root/build.sh && \
    /bin/sh ./root/build.sh && \
    rm -rf /root/*

# Start cowrie
ENV PYTHONPATH /home/cowrie/cowrie
WORKDIR /home/cowrie/cowrie
USER cowrie
CMD ["/usr/bin/twistd", "--nodaemon", "-y", "cowrie.tac", "--pidfile", "var/run/cowrie.pid", "cowrie"]