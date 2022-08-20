import asyncio
import aiohttp
import h3
from codetiming import Timer


async def worker_task(work_queue, out_stream):
    """
    fetches h3 indices & uses api to look up nearest coastal point, write result to <out_stream>
    """
    def nearest_coast_distance_url(h):
        center = h3.h3_to_geo(h)
        return f"http://0.0.0.0:8001/ne/nearest_coast.json?longitude={center[1]}&latitude={center[0]}"

    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            h = await work_queue.get()
            async with session.get(nearest_coast_distance_url(h)) as response:
                try:
                    center = h3.h3_to_geo(h)
                    r = await response.json()
                    if not r['ok'] or not r['rows'][0][0]:
                        raise Exception(f"error fetching index {h}, response: {r}")
                    out_stream.write(f"""{h}, {center[1]}, {center[0]}, {r['rows'][0][0]}\n""")
                except Exception as e:
                    print(f"error: {e}")
                    await work_queue.put(h)


async def produce_locations(work_queue, res: int, min_lon, max_lon, min_lat, max_lat):
    """
    produces a sequence of h3 indices at resolution <res> within specified bounds
    """

    def in_bounds(h):
        center = h3.h3_to_geo(h)
        return (center[1] >= min_lon) and (center[1] <= max_lon) and (center[0] >= min_lat) and (center[0] <= max_lat)

    indices: set = set()
    for h0 in h3.get_res0_indexes():
        indices = indices.union(set(h3.h3_to_children(h0, res)))
    return [await work_queue.put(h) for h in indices if in_bounds(h)]


async def main(res: int,
               min_lon: float = -180,
               max_lon: float = +180,
               min_lat: float = -90,
               max_lat: float = +90):

    work_queue = asyncio.Queue()
    print("running tasks...")
    with Timer(text="\nTotal elapsed time: {:.1f}"):
        with open(f"h3_r{res}.csv", "w") as outfile:
            outfile.write('"h3","longitude","latitude", "distance_to_coast"\n')
            producer = asyncio.create_task(produce_locations(work_queue, res, min_lon, max_lon, min_lat, max_lat))
            workers = [asyncio.create_task(worker_task(work_queue, outfile)) for i in range(3)]
            await asyncio.gather(*workers, producer)


if __name__ == "__main__":
    # asyncio.run(main(res=3, max_lat=42, min_lat=35, max_lon=30, min_lon=24))
    asyncio.run(main(res=0))
