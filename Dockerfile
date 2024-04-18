FROM python:3.11-alpine

WORKDIR /app

RUN pip install "psycopg[binary,pool]" flask flask_restful musicbrainzngs

COPY . .

EXPOSE 7000

ENTRYPOINT ["python", "main.py"]
