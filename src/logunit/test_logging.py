import asyncio
import socket
import pytest

import os

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

    server = await asyncio.start_unix_server(handle_log, "/tmp/logging.sock")

    async with server:
        await server.serve_forever()


@pytest.mark.asyncio
async def test_handler():
    '''
    Test the handler
    '''
    async def task():
        await asyncio.sleep(1)
        message = 'HELLO'
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect('/tmp/logging.sock')
            sock.sendall(message.encode())
            sock.close()
            
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(logging_mock())
            tg.create_task(task())
            await asyncio.sleep(2)
            tg.create_task(force_terminate_task_group())
    except* TerminateTaskGroup as e:    
        with open('unit.log', 'r') as f:
            lines = f.read()
        os.remove("unit.log")
        assert 'HELLO' in lines