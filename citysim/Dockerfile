FROM debian:latest
RUN apt-get update && apt-get install -y binutils wget
ADD install.sh /root/
RUN /root/install.sh

WORKDIR /opt/city
EXPOSE 8080
ENTRYPOINT ["/opt/city/citysim"]