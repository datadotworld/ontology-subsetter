# Dockerfile for FIBO subset webhook image

FROM python:3.7.2-alpine

RUN apk add --update curl && \
  pip install requests==2.21.0 Flask==1.0.2 rdflib==4.2.2 && \
  mkdir -p /subset-webhook && \
  cd /subset-webhook

COPY *.py /subset-webhook/

RUN curl -Os https://raw.githubusercontent.com/edmcouncil/ontology-publisher/master/publisher/lib/subset.py

WORKDIR /subset-webhook

CMD ["python", "webhook_app.py"]
