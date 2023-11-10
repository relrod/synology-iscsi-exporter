FROM python:3-alpine

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 19001

USER 1000

CMD [ "python3", "exporter.py" ]
