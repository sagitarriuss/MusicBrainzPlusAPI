FROM python:3.11-alpine

WORKDIR /app

RUN pip install "psycopg[binary,pool]"
RUN pip install flask
RUN pip install flask_restful
RUN pip install musicbrainzngs

COPY ./*.py ./
COPY ./*.ini ./
COPY ./*.txt ./

EXPOSE 7000

CMD ["python", "main.py"]