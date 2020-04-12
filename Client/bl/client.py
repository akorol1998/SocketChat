import asyncio
import json
import socket
from quamash import QEventLoop
from time import strftime, localtime
import websockets
from websockets.client import WebSocketClientProtocol
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK, ConnectionClosed

from Client.utils.client import BaseClient
from Client.interface.interface import ClientApplication

class Client(BaseClient):
	_websocket: WebSocketClientProtocol = None

	def __init__(self, app: ClientApplication=None, loop: QEventLoop=None):
		self._nick = None
		self._port = None
		self._host = None
		self._ws_url = None
		self.__loop = loop
		self.__application = app
		self.create_application()
	
	def create_application(self):
		self.__application.setup(self, self.__loop)
		
	async def start_messaging(self, ws: WebSocketClientProtocol, host: str, port: str, nick: str):
		self._nick = nick
		self._host = host
		self._port = port
		self._websocket = ws
		while True:
			try:
				data = await self._websocket.recv()
			except ConnectionClosedOK:
				await self.__application.connection_lost_handler()
				break
			else:
				await self.handle_response(data)
				
	async def send_message(self, typ: str="message", message: str=None, **kwargs):
		context = {
			"type": typ,
			"client": {
				"nick": self._nick,
				"message": message,
				"time": strftime("%H:%M", localtime())
			}
		}
		jeyson = json.dumps(context)
		await self._websocket.send(jeyson)

	async def handle_response(self, data: str):
		state = json.loads(data)
		if state['message_log']:
			self.__application.handle_message_log(state['message_log'])
		if state['new_user']:
			self.__application.handle_new_user(state['new_user'])
		if state['left_user']:
			self.__application.handle_left_user(state['left_user'])
		if state['client']:
			self.__application.print_message(state['client'])
		if state['user_list']:
			self.__application.handle_user_list(state['user_list'])
	
	async def establish_connection(self, host: str, port: str):
		try:
			ws = await asyncio.wait_for(websockets.connect(f"ws://{host}:{port}"), timeout=1)
			return ws
		except (asyncio.futures.TimeoutError, OSError):
			return None
		except socket.gaierror:
			return None
	
	async def validate_nickname(
		self,
		ws: WebSocketClientProtocol,
		nick: str,
		typ: str=None,
		message: str=None,
		**kwargs):
		context = {
			"type": typ,
			"client": {
				"nick": nick,
				"message": message,
				"time": strftime("%H:%M", localtime())
			}
		}
		jeyson = json.dumps(context)
		await ws.send(jeyson)
		res = json.loads(await ws.recv())
		return res
