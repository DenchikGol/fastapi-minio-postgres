FROM python:3.10.12-alpine3.18
LABEL maintainer="screenshots"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/"

RUN pip install --upgrade pip
COPY ./requirements.txt /tmp/requirements.txt
WORKDIR /api
EXPOSE 8000

# RUN apk add postgresql-client build-base postgresql-dev
RUN pip install -r /tmp/requirements.txt


RUN adduser --disabled-password --no-create-home fastapi
RUN chown -R fastapi:fastapi /api

USER fastapi

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
