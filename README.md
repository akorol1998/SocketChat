## Async Client - Server chat
This repository contains server and client sides of the application in Server and Client
directories respectively. The whole application is build on top of three major libraries:
'asyncio': library that allows to write concurrent code and use loop events
'websockets': library which handles socket connecitons, handshakes and data transfer
'PyQt5': which handles GUI part.

# 1. How to start with Docker
Make sure the docker is installed on your machine

# Run the following command in the terminal to Build an image

$docker build --tag server-image .

# Run container which in which your server will be launched

docker run --name server --rm -it -p8080:8080 server-image

# 2. Run in the venv

pip install --upgrade pip
pip install -r requirements.txt

# Launching the server

python3 Server/app.py

# Launching the client

python3 Client/app.py