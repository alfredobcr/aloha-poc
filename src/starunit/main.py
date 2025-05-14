"""
Star unit
"""
import asyncio
import csv
import json
from pathlib import Path


async def route_out(path, message, sleep=0.001):
    await asyncio.sleep(sleep)
    _, log_unit_input = \
        await asyncio.open_unix_connection(path)
    log_unit_input.write(message.encode())
    await log_unit_input.drain()
    log_unit_input.close()
    await log_unit_input.wait_closed()


async def star_data_row(queue: asyncio.Queue):
    """
    Process a row of star data
    """
    while True:
        message = await queue.get()
        await route_out("/tmp/log-star.sock", message)
        await route_out("/tmp/dropunit.sock", message)
        queue.task_done()


async def main(source: str):
    """
    Main Loop
    """
    queue = asyncio.Queue()

    with open(Path(__file__).parent / source, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            message = json.dumps(row)
            await queue.put(message)

    tasks = []
    for _ in range(3):
        task = asyncio.create_task(star_data_row(queue))
        tasks.append(task)

    await queue.join()
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main("btc.csv"))
