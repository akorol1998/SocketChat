import asyncio
import logging
import websockets
from functools import partial
from Server.bl.observer import Observable
from concurrent.futures.thread import ThreadPoolExecutor


async def command_line(self):
		loop = asyncio.get_event_loop()
		inp = partial(input, "command: ")
		exe = partial(loop.run_in_executor, ThreadPoolExecutor(1, thread_name_prefix='command_line'), inp)
		while True:
			try:
				res = await exe()
			except KeyboardInterrupt:
				print("raising")
				raise KeyboardInterrupt
			except EOFError:
				res = ""
			if res == 'exit':
				await self.shut_down()
			elif res == 'list':
				await self.list_users()
			elif res == 'help':
				print('Available commands:\n'\
					'exit - disconnects all the users and exits the server\n'\
					'list - lists all the connections\n'\
					'kill <name_of_the_user> - disconnects particular user, provided with the first argument\n'\
					'help - displays help menu')
			elif res.startswith('kill'):
				try:
					await self.kill(res)
				except IndexError:
					print("Not enough arguments")
				except websockets.ConnectionClosedError as e:
					logging.error(e)
				except websockets.ConnectionClosed:
					pass
			else:
				print("Invalid command, call 'help' for additional info.")