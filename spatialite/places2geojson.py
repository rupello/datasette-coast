import os
import sys
import json

def records(path):
    field_names = [
        'geonameid',
        'name',
        'asciiname',
        'alternatenames',
        'latitude',
        'longitude',
        'feature',
        'feature',
        'country',
        'cc2',
        'admin1',
        'admin2',
        'admin3',
        'admin4',
        'population',
        'elevation',
        'dem',
        'timezone',
        'modification',
    ]
    assert (os.path.exists(path))
    for line in open(path):
        yield dict(zip(field_names, line.split('\t')))


def record_to_geojson_feature(record):
    return {
        "id": int(record["geonameid"]),
        "type": "Feature",
        "properties": record,
        "geometry": {
            "coordinates": [float(record["longitude"]), float(record['latitude'])],
            "type": "Point"
            }
        }


def main(path):
    for r in records(path):
        print(json.dumps(record_to_geojson_feature(r)))


if __name__ == '__main__':
    main(sys.argv[1])

