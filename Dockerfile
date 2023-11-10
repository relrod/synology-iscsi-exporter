FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY requirements.txt exporter.py .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 19001

USER 1000

CMD [ "python3", "exporter.py" ]
