FROM docker.io/python:3.13.5-alpine

RUN adduser --no-create-home --disabled-password appuser && \
    apk update --no-cache

WORKDIR /app
ENV PYTHONUNBUFFERED=True

COPY src .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

USER appuser
CMD ["python", "main.py"]
