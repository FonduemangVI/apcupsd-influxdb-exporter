FROM python:2-alpine

COPY ./apcupsd-influxdb-exporter.py /apcupsd-influxdb-exporter.py
RUN pip install apcaccess influxdb

CMD ["python", "/apcupsd-influxdb-exporter.py"]
