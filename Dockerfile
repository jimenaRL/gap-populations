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

# install cargo and rut
RUN curl https://sh.rustup.rs -sSf > rustup.sh
RUN chmod 755 rustup.sh
RUN ./rustup.sh -y
# Add .cargo/bin to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# set python enviroment
ENV PYENV_ROOT=/root/.pyenv
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 3.10 && \
    pyenv global 3.10


# -----------------------------------------------------------------------------
#  Stage 2: user setup
# -----------------------------------------------------------------------------
FROM ubuntu:22.04

COPY --from=sqlite /usr/local/bin/sqlite3 /usr/local/bin/sqlite3
COPY --from=sqlite /usr/local/lib/libsqlite3.so.0 /usr/local/lib/libsqlite3.so.0

COPY --from=pyenv /root/.pyenv /root/.pyenv
ENV PYENV_ROOT=/root/.pyenv
ENV PATH=$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV PYTHONIOENCODING=utf-8

RUN apt-get update && \
    apt-get install build-essential -y && \
    apt-get install -y git && \
    apt-get install -y nano && \
    apt-get install -y curl && \
    apt-get install -y bc && \
    apt-get install -y zip && \
    apt-get install tree -y && \
    apt-get install -y openssh-client && \
    apt-get clean

# install cargo and rust
RUN curl https://sh.rustup.rs -sSf > rustup.sh
RUN chmod 755 rustup.sh
RUN ./rustup.sh -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN rustup default stable

# installing minet and xan
# COPY install_minet.sh install_minet.sh
# RUN ./install_minet.sh
# RUN cargo install xan

RUN pyenv global 3.10.10

#install latex
WORKDIR /tmp2
RUN curl -L -o install-tl-unx.tar.gz https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
RUN zcat < install-tl-unx.tar.gz | tar xf -
WORKDIR /tmp2/install-tl-20250409
RUN perl ./install-tl --no-interaction
ENV PATH="/usr/local/texlive/2025/bin/x86_64-linux:${PATH}"

RUN pip install latex

RUN mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts

WORKDIR /home/jimena/work/dev
RUN --mount=type=ssh git clone git@github.com:jimenaRL/gap-populations.git
WORKDIR /home/jimena/work/dev/gap-populations
RUN --mount=type=ssh git checkout main
RUN --mount=type=ssh git pull
RUN pip install -r python/requirements.txt

WORKDIR /home/jimena/work/dev
RUN --mount=type=ssh git clone git@github.com:jimenaRL/some4demDB.git
WORKDIR /home/jimena/work/dev/some4demDB
RUN --mount=type=ssh git checkout main
RUN --mount=type=ssh git pull
RUN pip install -r python/requirements.txt

WORKDIR /home/jimena/work/dev/gap-populations
RUN --mount=type=ssh git checkout main
RUN --mount=type=ssh git pull

# add python packages to PYTHONPATH
ENV PYTHONPATH=/home/jimena/work/dev/some4demDB/python:/home/jimena/work/dev/gap-populations/python

WORKDIR /home/jimena/work/dev/some4demDB

RUN mkdir -p tmp/gap-populations-outputs

RUN mkdir -p tmp/tmp/anonymized_exploitation
RUN mkdir -p tmp/tmp/anonymized_reproducibility
RUN mkdir -p tmp/tmp/lut
RUN mkdir -p tmp/tmp/pseudonymized_alldata
RUN mkdir -p tmp/tmp/pseudonymized_exploitation
RUN mkdir -p tmp/tmp/pseudonymized_reproducibility
RUN mkdir -p tmp/tmp/validations
RUN mkdir -p tmp/tmp/raw

RUN mkdir -p tmp/final_folder/anonymized_exploitation
RUN mkdir -p tmp/final_folder/anonymized_reproducibility
RUN mkdir -p tmp/final_folder/lut
RUN mkdir -p tmp/final_folder/pseudonymized_alldata
RUN mkdir -p tmp/final_folder/pseudonymized_exploitation
RUN mkdir -p tmp/final_folder/pseudonymized_reproducibility
RUN mkdir -p tmp/final_folder/raw
RUN mkdir -p tmp/final_folder/validations

RUN groupadd -g 1001 jimena
RUN useradd jimena -u 1001 -g 1001
RUN groupadd -g 1022 lut
RUN groupadd -g 1020 anonymized_exploitation
RUN groupadd -g 1021 anonymized_reproducibility
RUN groupadd -g 1023 pseudonymized_alldata
RUN groupadd -g 1024 pseudonymized_exploitation
RUN groupadd -g 1025 pseudonymized_reproducibility

WORKDIR /home/jimena/work/dev/gap-populations
RUN --mount=type=ssh git pull
RUN --mount=type=ssh git checkout loadEmbeddingsFromSqlite
