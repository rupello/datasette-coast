FROM python:3.9.13-slim-bullseye AS builder

RUN apt update

RUN apt install -y wget unzip spatialite-bin libsqlite3-mod-spatialite
RUN pip install geojson-to-sqlite

ADD spatialite/places2geojson.py .
ADD spatialite/places.sql .
ADD spatialite/etl.sh .
RUN ./etl.sh

FROM datasetteproject/datasette

COPY --from=builder ./ne.sqlite ./

ADD datasette/metadata.yaml metadata.yaml
ADD datasette/templates templates

CMD datasette -m /metadata.yaml -p 8001 -h 0.0.0.0 --template-dir=/templates --load-extension=spatialite /ne.sqlite