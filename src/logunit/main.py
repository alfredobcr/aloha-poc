'''
Logging unit
'''
import asyncio
import logging


logging.basicConfig(
    filename='unit.log', encoding='utf-8', level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
    '''
    Handle incoming connections
    '''
    data = await reader.read()
    message = data.decode()
    addr = writer.get_extra_info('peername')

    logging.info('Received %s from %s', message, addr)
    writer.close()
    await writer.wait_closed()


async def log_unit(log_layer: str):
    '''
    Single log unit
    '''
    server = await asyncio.start_unix_server(handler, path=f'/tmp/log-{log_layer}.sock')
    logging.info('Starting server on /tmp/log-%s.sock', log_layer)

    async with server:
        await server.serve_forever()


async def main():
    units = ['star', 'dropunit', 'maxreducerunit', 'avgreducerunit', 'minreducerunit']
    async with asyncio.TaskGroup() as tg:
        for unit in units:
            tg.create_task(log_unit(unit))

if __name__ == '__main__':
    asyncio.run(main())
