# 狐狸OS Docker Hub 试用镜像：用 cloud-hypervisor + 宿主 KVM 引导 *真正的* ISO。
# 这是分发通道，不是狐狸OS 的运行时，也不在容器里画假桌面。
# 不要在本仓库里保存 Docker Hub 密码；推送前需 Sarah 登录。
FROM debian:bookworm-slim

ARG CLOUD_HYPERVISOR_VERSION=v46.0
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates wget xorriso iproute2 iptables python3 python3-websockify novnc \
    && rm -rf /var/lib/apt/lists/*

# 官方静态二进制（Apache-2.0），与 ISO 里打包的是同一条线。
RUN mkdir -p /usr/lib/foxos/vmm \
 && wget -O /usr/lib/foxos/vmm/cloud-hypervisor \
      "https://github.com/cloud-hypervisor/cloud-hypervisor/releases/download/${CLOUD_HYPERVISOR_VERSION}/cloud-hypervisor-static" \
 && chmod 755 /usr/lib/foxos/vmm/cloud-hypervisor \
 && printf '%s\n' \
      "cloud-hypervisor ${CLOUD_HYPERVISOR_VERSION}" \
      "https://github.com/cloud-hypervisor/cloud-hypervisor" \
      "Licensed under the Apache License, Version 2.0." \
    > /usr/lib/foxos/vmm/NOTICE

COPY docker/os/entrypoint-trial.sh /usr/local/bin/foxos-docker-trial
RUN chmod 755 /usr/local/bin/foxos-docker-trial

EXPOSE 5900 6080
VOLUME ["/var/lib/foxos"]
ENTRYPOINT ["/usr/local/bin/foxos-docker-trial"]
