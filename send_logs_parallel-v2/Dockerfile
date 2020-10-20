FROM python:alpine3.7
COPY . /app
WORKDIR /app
ENV messages_per_second 1
CMD python  ./main.py ${messages_per_second} ${loop}
