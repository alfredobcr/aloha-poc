import asyncio
import os
import socket
import json
import pytest

from dropunit.main import main


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

    server = await asyncio.start_unix_server(handle_log, "/tmp/log-dropunit.sock")

    async with server:
        await server.serve_forever()

@pytest.mark.asyncio
async def test_drop_unit_data():

    async def task():
        
        message = {
            "unix": "1628104740", 
            "date": "2021-08-04 19:19:00", 
            "symbol": "BTC/USD", 
            "open": "39724.65", 
            "high": "39728.40", 
            "low": "39719.38", 
            "close": "39726.21", 
            "Volume BTC": "0.48128564", 
            "Volume USD": "19119.6544046244"}
        await asyncio.sleep(1)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/tmp/dropunit.sock')
            sock.sendall(json.dumps(message).encode())
            sock.close()

    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(main())
            tg.create_task(logging_mock())
            tg.create_task(task())
            await asyncio.sleep(3)
            tg.create_task(force_terminate_task_group())
    except* TerminateTaskGroup as e:    
        with open('unit.log', 'r') as f:
            lines = f.read()
        dropping_fields = ["Volume BTC", "Volume USD", "high", "low", "close", "symbol"]
        for field in dropping_fields:
            assert field not in lines
        os.remove("unit.log")