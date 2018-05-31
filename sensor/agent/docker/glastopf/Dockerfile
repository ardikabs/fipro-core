FROM alpine 

# Include dist and build script
ADD dist/ /root/dist/
COPY build.sh /root/

# Install dependencies, packages and glastopf
RUN chmod +x /root/build.sh && \
    /bin/sh ./root/build.sh && \
    rm -rf /root/*

# Start glastopf
WORKDIR /opt/glastopf
# ENTRYPOINT add config file every container is started
CMD ["glastopf-runner"]