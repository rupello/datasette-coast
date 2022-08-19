#   .loadshp ne_110m_coastline/ne_110m_coastline coast utf-8
docker run -p 8001:8001 -v $(pwd)/datasette:/mnt datasetteproject/datasette datasette -m /mnt/metadata.yaml --template-dir=/mnt/templates/ -p 8001 -h 0.0.0.0 /mnt/ne.sqlite --load-extension=spatialite
