FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY server.py /app/

ENTRYPOINT ["python", "server.py"]
