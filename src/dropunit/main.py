"""
Dropping Unit module
"""
import asyncio
import json


async def route_out(path, message, sleep=0.001):
    await asyncio.sleep(sleep)
    _, log_unit_input = \
        await asyncio.open_unix_connection(path)
    log_unit_input.write(message.encode())
    await log_unit_input.drain()
    log_unit_input.close()
    await log_unit_input.wait_closed()


async def handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
    ):
    dropping_fields = ["Volume BTC", "Volume USD", "high", "low", "close", "symbol"]
    data = await reader.read()
    message = data.decode()
    payload = json.loads(message)
    for field in dropping_fields:
        _ = payload.pop(field)
    await route_out("/tmp/log-dropunit.sock", json.dumps(payload))
    await route_out("/tmp/maxreducerunit.sock", json.dumps(payload))
    await route_out("/tmp/minreducerunit.sock", json.dumps(payload))
    await route_out("/tmp/avgreducerunit.sock", json.dumps(payload))

async def main():
    server = await asyncio.start_unix_server(handler, path='/tmp/dropunit.sock')

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())