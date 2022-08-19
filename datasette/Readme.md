
```sql
select distance, AsGeoJSON(st_shortestline(makepoint(-4.8,51),geometry)) from knn join coast as c on knn.fid = c.rowid where f_table_name = 'coast' and ref_geometry = MakePoint(-4.8, 51) and max_items = 1;
```

```shell
curl http://0.0.0.0:8001/coast/nearest_coast.json\?longitude\=-4.3\&latitude\=52 | jq .
```