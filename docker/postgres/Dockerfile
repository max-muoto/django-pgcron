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

# Build pg_cron. LLVM bitcode (JIT) is skipped: with_llvm defaults to yes, so
# PGXS compiles each object to a .bc bitcode file using the exact compiler
# recorded in Makefile.global (CLANG=clang-21 -- the one postgres:17-alpine was
# built with), which the runtime image does not ship. `apk add clang` installs a
# newer clang (clang-22), so the build fails with "clang-21: No such file or
# directory". with_llvm=no skips the .bc targets instead of pinning a compiler.
#   https://www.postgresql.org/docs/17/jit.html
#   https://github.com/postgres/postgres/blob/REL_17_STABLE/src/makefiles/pgxs.mk#L221-L223
RUN curl -L https://github.com/citusdata/pg_cron/archive/v1.6.8.tar.gz | tar xz && \
    cd pg_cron-1.6.8 && \
    make with_llvm=no && \
    make install with_llvm=no && \
    cd .. && \
    rm -rf pg_cron-1.6.8

# remove build tools to reduce image size
RUN apk del git make gcc clang llvm musl-dev postgresql17-dev

COPY init-pgcron.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-pgcron.sh
