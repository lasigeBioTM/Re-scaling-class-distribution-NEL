FROM python:3.7

RUN apt-get update && apt-get install -y git && apt-get autoclean -y
RUN apt-get update && apt-get install -y wget && apt-get autoclean -y
RUN apt-get update && apt-get install -y nano && apt-get autoclean -y
RUN apt-get update && apt-get install -y vim && apt-get autoclean -y
RUN apt-get update && apt install unzip && apt-get autoclean -y 

# Java
RUN apt-get update && apt-get install -y default-jdk && apt-get autoclean -y

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt


WORKDIR REEL_NILINKER

