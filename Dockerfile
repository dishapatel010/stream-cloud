FROM python:3.9.1-buster

ENV VIRTUAL_ENV "/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get upgrade -y
RUN python -m pip install --upgrade pip

WORKDIR /usr/src/app

COPY . .

RUN pip install -U -r requirements.txt

CMD ./start.sh
