import asyncio
import aiohttp
import h3
from codetiming import Timer


def h3_indices_at_res(res: int,
                      min_lon: float = -180,
                      max_lon: float = +180,
                      min_lat: float = -90,
                      max_lat: float = +90):
    def in_bounds(h):
        center = h3.h3_to_geo(h)
        return (center[1] >= min_lon) and (center[1] <= max_lon) and (center[0] >= min_lat) and (center[0] <= max_lat)

    indices: set = set()
    for h0 in h3.get_res0_indexes():
        indices = indices.union(set(h3.h3_to_children(h0, res)))
    return [h for h in indices if in_bounds(h)]


def nearest_coast_distance_url(h):
    center = h3.h3_to_geo(h)
    return f"http://0.0.0.0:8001/ne/nearest_coast.json?longitude={center[1]}&latitude={center[0]}"


async def fetch_task(name, work_queue, result_queue):
    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            h = await work_queue.get()
            async with session.get(nearest_coast_distance_url(h)) as response:
                try:
                    center = h3.h3_to_geo(h)
                    r = await response.json()
                    if not r['ok'] or not r['rows'][0][0]:
                        raise Exception(f"error fetching index {h}, response: {r}")
                    await result_queue.put(f"""{h}, {center[1]}, {center[0]}, {r['rows'][0][0]}""")
                except Exception as e:
                    print(f"error: {e}")
                    await work_queue.put(h)


async def write_task(file_path, result_queue):
    with open(file_path, "w") as f:
        while True:
            result = await result_queue.get()
            if result == "done":
                break
            f.write(result + "\n")


async def main(res: int,
               min_lon: float = -180,
               max_lon: float = +180,
               min_lat: float = -90,
               max_lat: float = +90):

    work_queue = asyncio.Queue()
    result_queue = asyncio.Queue()

    print("computing tasks...")
    for h in h3_indices_at_res(res, min_lon, max_lon, min_lat, max_lat):
        await work_queue.put(h)

    print("running tasks...")
    with Timer(text="\nTotal elapsed time: {:.1f}"):
        await result_queue.put('"h3","longitude","latitude", "distance_to_coast"')
        writer = asyncio.create_task(write_task(f"h3_r{res}.csv", result_queue))
        await asyncio.gather(
            asyncio.create_task(fetch_task("One", work_queue, result_queue)),
            asyncio.create_task(fetch_task("Two", work_queue, result_queue)),
            asyncio.create_task(fetch_task("Three", work_queue, result_queue)),
        )
        await result_queue.put('done')
        await asyncio.wait_for(writer, timeout=1e6)


if __name__ == "__main__":
    asyncio.run(main(res=6, max_lat=42, min_lat=35, max_lon=30, min_lon=24))
