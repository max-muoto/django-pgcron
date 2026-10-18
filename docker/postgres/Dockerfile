ARG PG_VERSION=17
FROM postgres:${PG_VERSION}-alpine

# Use the image's server headers and matching Clang/LLVM toolchain.
RUN apk add --no-cache \
      git \
      make \
      gcc \
      $DOCKER_PG_LLVM_DEPS \
      musl-dev \
      curl

# Build pg_cron
RUN curl -fL https://github.com/citusdata/pg_cron/archive/v1.6.8.tar.gz | tar xz && \
    cd pg_cron-1.6.8 && \
    make  && \
    make install && \
    cd .. && \
    rm -rf pg_cron-1.6.8

# remove build tools to reduce image size
RUN apk del git make gcc $DOCKER_PG_LLVM_DEPS musl-dev

COPY init-pgcron.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-pgcron.sh
