import json
import asyncio

import pytest
import os

from starunit.main import main


class TerminateTaskGroup(Exception):
    '''
    Exception to terminate the task group
    '''
    pass


async def force_terminate_task_group():
    '''
    Force terminate the task group
    '''
    raise TerminateTaskGroup('Force terminate the task group')


async def logging_mock():
    async def handle_log(reader, writer):
        data = await reader.read()
        message = data.decode()

        with open("unit.log", "w", encoding="utf-8") as f:
            print(message, file=f)
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_unix_server(handle_log, "/tmp/log-star.sock")

    async with server:
        await server.serve_forever()


@pytest.mark.asyncio
async def test_log_star_data():

    keys = "unix,date,symbol,open,high,low,close,Volume BTC,Volume USD".split(",")
    values = "1646106180,2022-03-01 03:43:00,BTC/USD,43046.58,43046.58,43046.58,43046.58,0.00000000,0.0".split(",")
    payload = dict(zip(keys, values))
    message = json.dumps(payload)
    
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(logging_mock())
            tg.create_task(main("test-btc.csv"))
            await asyncio.sleep(3)
            tg.create_task(force_terminate_task_group())
    except* TerminateTaskGroup as e:    
        with open('unit.log', 'r') as f:
            lines = f.read()
        assert message in lines
        os.remove("unit.log")