FROM astrocrpublic.azurecr.io/runtime:3.2-4

USER root

RUN apt-get update && \
    apt-get install -y openjdk-21-jre-headless && \
    apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

USER astro