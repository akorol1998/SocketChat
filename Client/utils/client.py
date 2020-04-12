from typing import Any
from abc import ABC, abstractmethod


class BaseClient(ABC):
	
	@abstractmethod
	async def start_messaging(self, ws, host, port, nick):
		pass

	@abstractmethod
	async def send_message(self, type, message, **kwargs):
		pass

	@abstractmethod
	async def handle_response(self, data: Any):
		pass

	@abstractmethod
	async def establish_connection(self, host, port):
		pass
