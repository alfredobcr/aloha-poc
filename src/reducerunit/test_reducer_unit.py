import asyncio
import pytest
import os
import json

from reducerunit import main


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

async def logging_mock(config: str):
    async def handle_log(reader, writer):
        data = await reader.read()
        message = data.decode()

        with open("unit.log", "w", encoding="utf-8") as f:
            print(message, file=f)
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_unix_server(handle_log, f"/tmp/log-{config}reducerunit.sock")

    async with server:
        await server.serve_forever()


@pytest.mark.asyncio
async def test_min_handler():
    '''
    Test the min handler unit
    '''
    payload = {
            "unix": "1628104740", 
            "date": "2021-08-04 19:19:00", 
            "symbol": "BTC/USD", 
            "open": "39724.65", 
            "high": "39728.40", 
            "low": "39719.38", 
            "close": "39726.21", 
            "Volume BTC": "0.48128564", 
            "Volume USD": "19119.6544046244"}
    message = json.dumps(payload)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(logging_mock("min"))
            tg.create_task(main.min_reducer_unit())
            tg.create_task(main.route_out("/tmp/minreducerunit.sock", message))
            await asyncio.sleep(2)
            tg.create_task(force_terminate_task_group())
    except* TerminateTaskGroup as e:    
        with open('unit.log', 'r') as f:
            lines = f.read()
        os.remove("unit.log")
        assert 'New Min' in lines


@pytest.mark.asyncio
async def test_max_handler():
    '''
    Test the min handler unit
    '''
    payload = {
            "unix": "1628104740", 
            "date": "2021-08-04 19:19:00", 
            "symbol": "BTC/USD", 
            "open": "39724.65", 
            "high": "39728.40", 
            "low": "39719.38", 
            "close": "39726.21", 
            "Volume BTC": "0.48128564", 
            "Volume USD": "19119.6544046244"}
    message = json.dumps(payload)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(logging_mock("max"))
            tg.create_task(main.max_reducer_unit())
            tg.create_task(main.route_out("/tmp/maxreducerunit.sock", message))
            await asyncio.sleep(2)
            tg.create_task(force_terminate_task_group())
    except* TerminateTaskGroup as e:    
        with open('unit.log', 'r') as f:
            lines = f.read()
        os.remove("unit.log")
        assert 'New Max' in lines


@pytest.mark.asyncio
async def test_avg_handler():
    '''
    Test the min handler unit
    '''
    payload = {
            "unix": "1628104740", 
            "date": "2021-08-04 19:19:00", 
            "symbol": "BTC/USD", 
            "open": "39724.65", 
            "high": "39728.40", 
            "low": "39719.38", 
            "close": "39726.21", 
            "Volume BTC": "0.48128564", 
            "Volume USD": "19119.6544046244"}
    message = json.dumps(payload)
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(logging_mock("avg"))
            tg.create_task(main.avg_reducer_unit())
            tg.create_task(main.route_out("/tmp/avgreducerunit.sock", message))
            await asyncio.sleep(2)
            tg.create_task(force_terminate_task_group())
    except* TerminateTaskGroup as e:    
        with open('unit.log', 'r') as f:
            lines = f.read()
        os.remove("unit.log")
        assert 'New Avg' in lines