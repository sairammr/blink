FROM rust:1.83

RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get update && apt-get install -y \
    nodejs \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    build-essential \
    libsoup-3.0-dev \
    libwebkit2gtk-4.1-dev \
    libjavascriptcoregtk-4.1-dev \
    clang \
    libclang-dev \
    llvm \
    llvm-dev \
    cmake \
    pkg-config \
    libopencv-dev \
    python3-opencv && \
    apt-get clean


RUN cargo install tauri-cli
RUN npm install bun -g
WORKDIR /app

COPY *.json ./

RUN npm install

COPY src ./src
COPY src-tauri ./src-tauri
COPY public public
COPY *ts ./
COPY index.html ./
ENV LLVM_CONFIG=/usr/bin/llvm-config
ENV LIBCLANG_PATH=/usr/lib/llvm-12/lib
