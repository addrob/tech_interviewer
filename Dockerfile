FROM python:3.11.4-bullseye
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR tech_interviewer
COPY requirements.txt .
RUN apt-get update \
    && apt-get -y install libpq-dev gcc

RUN pip install -r requirements.txt
COPY . .

CMD python main.py