import sys
import asyncio
import json
import websockets
import logging
from functools import partial
from concurrent.futures.thread import ThreadPoolExecutor

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets import WebSocketServerProtocol

from Server.bl.observer import Observable, ChatObserver
from Server.config import LOG_FILE_PATH, NUM_OF_CONNECTTIONS


class Server:

	def __init__(self, host: str, port: int):
		self.__port = port
		self.__host = host
		logging.basicConfig(
			filename=LOG_FILE_PATH,
			level=logging.ERROR,
			format=format('%(asctime)s:%(levelname)s:%(message)s')
		)
		print(f"Starting server on {self.__host}:{self.__port}")

	async def launch_chat(self, data: dict, websocket: WebSocketServerProtocol):
		obs = ChatObserver(data, websocket)
		await Observable.attach(obs)
		try:
			while True:
				raw_data = await websocket.recv()
				data = await self.process_request(websocket, raw_data)
		except (ConnectionClosedError) as e:
			await Observable.detach(obs)	
			logging.error(e)
		except (ConnectionClosedOK) as ok:
			pass
		except SystemExit:
			pass
		finally:
			pass
			

	async def init_connection(self, websocket: WebSocketServerProtocol, path: str):
		try:
			while True:
				raw_data = await websocket.recv()
				result = await self.process_request(websocket, raw_data)
				if result:
					break
			data = json.loads(raw_data)
			await self.launch_chat(data, websocket)
		except (ConnectionClosedError, ConnectionClosedOK) as e:
			logging.error(e)


	def nick_available(self, nick_list: list, nick: str):
		return nick not in nick_list

	def valid_connection_quantity(self, server_num: int):
		return server_num < NUM_OF_CONNECTTIONS

	async def process_request(self, websocket: WebSocketServerProtocol, raw_data: str):
		print("raw_data", raw_data, type(raw_data))
		data = json.loads(raw_data)
		response = None
		if data['type'] == 'connection':
			nick_list = await Observable.get_nicknames()
			result = self.nick_available(nick_list, data['client']['nick'])
			server_num = await Observable.connection_nums()
			result2 = self.valid_connection_quantity(server_num)
			response = json.dumps({
				"nickname": result,
				"max_client": result2})
			# TODO create_task
			await websocket.send(response)
			return result and result2
		elif data['type'] == 'message':
			await Observable.incomming_message(data)
			return response
		return response

	async def list_users(self):
		[print(nick) for nick in await Observable.get_nicknames()]

	async def kill(self, command):
		sp = command.split()
		nick_list = await Observable.get_nicknames()
		if not self.nick_available(nick_list, sp[1]):
			obs = await Observable.get_by_name(sp[1])
			await Observable.disconnect_observer(obs)
			await Observable.detach(obs)

	async def shut_down(self):
		await Observable.disconnect_all()
		sys.exit(0)


