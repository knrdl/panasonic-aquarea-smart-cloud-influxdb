# panasonic-aquarea-smart-cloud-influxdb
Write heatpump values from cloud into an influxdb

```yaml
services:
  collector:
    image: ghcr.io/knrdl/panasonic-aquarea-smart-cloud-influxdb:edge
    restart: always
    environment:
      INFLUXDB_V2_URL: http://influxdb:8086
      INFLUXDB_V2_ORG: org0  # organisation
      INFLUXDB_V2_BUCKET: bucket0  # any bucket name
      INFLUXDB_V2_TOKEN: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  # needs write permissions for the bucket
      CLOUD_USERNAME: user@email.org  # mail addr
      CLOUD_PASSWORD: XXXXXXXXXXXXXXXXXXX
      LOAD_HISTORIC_DATA: 'true'  # necessary only once
    networks:
      - db  # shared network with the influxdb
    cpus: 1
    mem_limit: 250m
```