FROM postgres:17-alpine

# Install everything needed, including clang/llvm
RUN apk add --no-cache \
      git \
      make \
      gcc \
      clang \
      llvm \
      musl-dev \
      postgresql17-dev \
      curl

# Build pg_cron
RUN curl -L https://github.com/citusdata/pg_cron/archive/v1.6.4.tar.gz | tar xz && \
    cd pg_cron-1.6.4 && \
    make  && \
    make install && \
    cd .. && \
    rm -rf pg_cron-1.6.4

# remove build tools to reduce image size
RUN apk del git make gcc clang llvm musl-dev postgresql17-dev

COPY init-pgcron.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-pgcron.sh
