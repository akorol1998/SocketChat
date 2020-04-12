import asyncio
import websockets

from Server.config import PORT, HOST, LOCAL_HOST
from Server.bl.server import Server
from Server.commands import command_line

def main():
	app_server = Server(LOCAL_HOST, PORT)
	loop = asyncio.get_event_loop()
	server = websockets.serve(app_server.init_connection, host=LOCAL_HOST, port=PORT)
	try:
		loop.run_until_complete(server)
		loop.run_until_complete(command_line(app_server))
	except KeyboardInterrupt:
		pass
	else:
		loop.run_forever()


if __name__ == "__main__":
	main()
