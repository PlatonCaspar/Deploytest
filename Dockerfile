FROM ubuntu:yakkety
MAINTAINER Philipp Weißmann "mail@philipp-weissmann.de"
RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
COPY . /app
WORKDIR /app
RUN pip3 install pip --upgrade
RUN pip3 install -r requirements.txt --upgrade
ENTRYPOINT ["python3"]
CMD ["Platinen.py"]
