#!/usr/bin/env bash

# natural earth coastlines
wget --quiet https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/physical/ne_10m_coastline.zip
unzip ne_10m_coastline.zip
# load directly as shapefile & index
spatialite ne.sqlite << _commands
-- load shapefile
.loadshp ne_10m_coastline ne_10m_coastline utf-8 4326
select CreateSpatialIndex("ne_10m_coastline", "geometry");
_commands

# get geonames populated places http://download.geonames.org/export/dump/readme.txt
wget --quiet http://download.geonames.org/export/dump/cities1000.zip
unzip cities1000.zip
echo "converting to geojson..."
python places2geojson.py cities1000.txt > cities1000.geojson
echo "ingesting to sqlite..."
geojson-to-sqlite --nl --pk=id --spatialite ne.sqlite cities1000 cities1000.geojson
spatialite ne.sqlite << _commands
select CreateSpatialIndex("cities1000", "geometry");
_commands