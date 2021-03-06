#!/usr/bin/python
import os
import time

from apcaccess import status as apc
from influxdb import InfluxDBClient

apcport = int(os.getenv('APCUPSD_PORT'))
dbname = os.getenv('INFLUXDB_DATABASE', 'apcupsd')
user = os.getenv('INFLUXDB_USER')
password = os.getenv('INFLUXDB_PASSWORD')
port = os.getenv('INFLUXDB_PORT', 8086)
host = os.getenv('INFLUXDB_HOST', '10.0.1.9')
interval = float(os.getenv('INTERVAL', 5))
client = InfluxDBClient(host, port, user, password, dbname)
ups_alias = os.getenv('UPS_ALIAS','none')

client.create_database(dbname)

# Print envs
print("INFLUXDB_DATABASE: ", dbname)
print("INFLUXDB_USER: ", user)
print("INFLUXDB_PASSWORD: ", password)
print("INFLUXDB_PORT: ", port)
print("INFLUXDB_HOST: ", host)
print("UPS_ALIAS", ups_alias)
print("INTERVAL: ", interval)
print("APCUPSD_HOST", os.getenv('APCUPSD_HOST', 'localhost'))
print("VERBOSE: ", os.getenv('VERBOSE', 'localhost'))

while True:
    ups = apc.parse(apc.get(host=os.getenv('APCUPSD_HOST', 'localhost'), port=apcport), strip_units=True)
    watts = float(os.getenv('WATTS', ups.get('NOMPOWER', 0.0))) * 0.01 * float(ups.get('LOADPCT', 0.0))
    json_body = [
        {
            'measurement': 'apcaccess_status',
            'fields': {
                'WATTS': watts,
                'STATUS': ups.get('STATUS'),
                'LOADPCT': float(ups.get('LOADPCT', 0.0)),
                'BCHARGE': float(ups.get('BCHARGE', 0.0)),
                'TONBATT': float(ups.get('TONBATT', 0.0)),
                'TIMELEFT': float(ups.get('TIMELEFT', 0.0)),
                'NOMPOWER': float(ups.get('NOMPOWER', 0.0)),
                'CUMONBATT': float(ups.get('CUMONBATT', 0.0)),
                'BATTV': float(ups.get('BATTV', 0.0)),
                'OUTPUTV': float(ups.get('OUTPUTV', 0.0)),
                'ITEMP': float(ups.get('ITEMP', 0.0)),
            },
            'tags': {
                'host': os.getenv('HOSTNAME', ups.get('HOSTNAME', 'apcupsd-influxdb-exporter')),
                'serial': ups.get('SERIALNO', None),
                'ups_alias' : ups_alias,
            }
        }
    ]

    if os.getenv('VERBOSE', 'false').lower() == 'true':
        print(json_body)
        print(client.write_points(json_body))
    else:
        client.write_points(json_body)
    time.sleep(interval)