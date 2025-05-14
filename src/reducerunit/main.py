"""
Reducer Unit
"""
import asyncio
import json

from .cache import MinReducerCache, MaxReducerCache, AvgReducerCache


async def route_out(path, message, sleep=0.001):
    await asyncio.sleep(sleep)
    _, log_unit_input = \
        await asyncio.open_unix_connection(path)
    log_unit_input.write(message.encode())
    await log_unit_input.drain()
    log_unit_input.close()
    await log_unit_input.wait_closed()


async def reducer_config(config: str):
    reducers = {
        "max": max_reducer,
        "min": min_reducer,
        "avg": avg_reducer,
    }
    if config not in reducers:
        return None
    return reducers.get(config)


async def avg_reducer(payload: dict):
    
    minning_value = float(payload["open"])
    minned_value = AvgReducerCache(minning_value)
    result = sum([minned_value.value, minning_value]) / 2.0
    minned_value.set_cache(result)
    await route_out(
        "/tmp/log-avgreducerunit.sock", f"New Avg is: {minned_value.value}"
    )

async def min_reducer(payload: dict):
    minned_value = MinReducerCache(99999999999)
    minning_value = float(payload["open"])
    result = min(minned_value.value, minning_value)
    minned_value.set_cache(result)
    await route_out(
        "/tmp/log-minreducerunit.sock", f"New Min is: {minned_value.value}"
    )


async def max_reducer(payload: dict):
    maxed_value = MaxReducerCache(0)
    maxing_value = float(payload["open"])
    result = max(maxed_value.value, maxing_value)
    maxed_value.set_cache(result)
    await route_out(
        "/tmp/log-maxreducerunit.sock", f"New Max is: {maxed_value.value}"
    )


async def handler(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        config: str
    ):
    data = await reader.read()
    message = data.decode()
    payload = json.loads(message)
    reducer_fn = await reducer_config(config)
    await reducer_fn(payload)
    writer.close()
    await writer.wait_closed()


async def max_handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
    await handler(reader, writer, "max")


async def min_handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
    await handler(reader, writer, "min")


async def avg_handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
    await handler(reader, writer, "avg")

async def max_reducer_unit():
    server = await asyncio.start_unix_server(
        max_handler, path="/tmp/maxreducerunit.sock")

    async with server:
        await server.serve_forever()


async def min_reducer_unit():
    server = await asyncio.start_unix_server(
        min_handler, path="/tmp/minreducerunit.sock")
    async with server:
        await server.serve_forever()


async def avg_reducer_unit():
    server = await asyncio.start_unix_server(
        avg_handler, path="/tmp/avgreducerunit.sock")
    async with server:
        await server.serve_forever()


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(min_reducer_unit())
        tg.create_task(max_reducer_unit())
        tg.create_task(avg_reducer_unit())

if __name__ == "__main__":
    asyncio.run(main())
