FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    openssh-server \
    python3-websockify \
    netcat-openbsd \
    sudo \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd
# ប្ដូរ 'MyPassword123' ទៅជា Password SSH ដែលអ្នកចង់ប្រើ
RUN echo 'root:MyPassword123' | chpasswd 
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
