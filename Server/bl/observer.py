from __future__ import annotations
from typing import List, OrderedDict
from asyncio import Future, create_task
from websockets import WebSocketServerProtocol
import asyncio
import json
import logging

from Server.utils.utils import AsyncObservable, AsyncObserver
from Server.config import NUM_OF_MESSAGES


class ChatObservable(AsyncObservable):
	_observers: set = set()
	_message_log: list = []
	_num_observers: int = 0

	async def disconnect_all(self):
		[await obs.close() for obs in self._observers]

	async def disconnect_observer(self, observer: ChatObserver):
		await observer.close()
	
	async def connection_nums(self):
		return self._num_observers
			
	async def get_nicknames(self) -> List[str]:
		return [obs.nick for obs in self._observers]
	
	async def get_by_name(self, nick: str) -> AsyncObserver:
		for obs in self._observers:
			if obs.nick == nick:
				return obs

	async def attach(self, observer: AsyncObserver):
		await self.notify(obs_set=self._observers, new_user=observer.nick)
		self._observers.add(observer)
		self._num_observers += 1
		await self.notify(obs_set=set([observer]), user_list=self._observers, message_log=True)

	async def detach(self, observer: AsyncObserver):
		try:
			self._observers.remove(observer)
			self._num_observers -= 1
			await self.notify(obs_set=self._observers, left_user=observer.nick)
		except KeyError as e:
			logging.error(e)

	async def incomming_message(self, data: dict):
		await self.notify(obs_set=self._observers, client=data['client'])

	async def notify(
		self,
		obs_set: set=None,
		user_list: set=None,
		new_user: str=None,
		left_user: str=None,
		client: dict={},	
		message_log: bool=False,
		typ: str=None,
		**kwargs
	):
		if client:
			await create_task(self.log_the_message(client))
		context = {
			'user_list': [notif.nick for notif in user_list] if user_list else [],
			'new_user': new_user,
			'left_user': left_user,
			'message_log': self._message_log if message_log else [],
			'client': client,
			'type': typ
		}
		if obs_set:
			for obs in obs_set:
				await create_task(obs.update(context))

	async def log_the_message(self, client: dict):
		self._message_log.append(client)
		if len(self._message_log) == NUM_OF_MESSAGES + 1:
			self._message_log = self._message_log[1:]


class ChatObserver(AsyncObserver):

	def __init__(self, data: dict, ws: WebSocketServerProtocol):
		self.nick: str = data["client"]["nick"]
		self.ws: WebSocketServerProtocol = ws

	async def update(self, state: dict):
		obj = json.dumps(state)
		await self.ws.send(obj)
	
	async def close(self):
		await self.ws.close()

Observable = ChatObservable()
