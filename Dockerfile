# Inspired from https://github.com/KEINOS/Dockerfile_of_SQLite3
# -----------------------------------------------------------------------------
#  Stage 0: build sqlite binary
# -----------------------------------------------------------------------------
FROM ubuntu:22.04 AS sqlite

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# install sqlite

RUN apt-get update && \
    apt-get install build-essential -y && \
    apt-get install wget -y
RUN wget https://www.sqlite.org/2023/sqlite-autoconf-3410100.tar.gz
RUN tar -xvf sqlite-autoconf-3410100.tar.gz
RUN ./sqlite-autoconf-3410100/configure && \
    make && \
    make install

# -----------------------------------------------------------------------------
#  Stage 1: install pyenv
# -----------------------------------------------------------------------------
FROM ubuntu:22.04 AS pyenv

ENV DEBIAN_FRONTEND=noninteractive

# install pyenv with pyenv-installer
COPY pyenv_dependencies.txt pyenv_dependencies.txt

ENV PYENV_GIT_TAG=v2.3.14

RUN apt-get update && \
    apt-get install -y $(cat pyenv_dependencies.txt) && \
    apt-get install curl -y
RUN curl https://pyenv.run | bash
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 3.10 && \
    pyenv global 3.10


# -----------------------------------------------------------------------------
#  Stage 2: user setup
# -----------------------------------------------------------------------------
FROM ubuntu:22.04

COPY --from=sqlite /usr/local/bin/sqlite3 /usr/local/bin/sqlite3
COPY --from=sqlite /usr/local/lib/libsqlite3.so.0 /usr/local/lib/libsqlite3.so.0

COPY --from=pyenv /root/.pyenv /root/.pyenv
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV PYTHONIOENCODING utf-8

RUN apt-get update && \
    apt-get install build-essential -y

RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y nano && \
    apt-get install -y curl && \
    apt-get install -y bc && \
    apt-get install -y zip

# install cargo and rust
RUN curl https://sh.rustup.rs -sSf > rustup.sh
RUN chmod 755 rustup.sh
RUN ./rustup.sh -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN rustup default stable

# installing minet and xan
RUN cargo install xan

# clone project repo and install dependencies
ARG token
ENV env_token $token

WORKDIR /home/jimena/work/dev

RUN git clone https://${env_token}@github.com/jimenaRL/gap-populations.git

RUN git pull

WORKDIR /home/jimena/work/dev/gap-populations

# RUN pip install -r python/requirements.txt

# add symlink to python packages

