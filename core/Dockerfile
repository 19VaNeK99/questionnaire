FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /core
WORKDIR /core
COPY requirements.txt /core/
RUN pip install -r requirements.txt
COPY . /core/