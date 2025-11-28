FROM busybox:latest

WORKDIR /usr/local/bin/bootstrap

COPY bootstrap/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
