FROM python:3

WORKDIR /usr/src/server

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080/tcp

ENV PYTHONPATH="${PYTHONPATH}:/usr/src/server"

COPY . .
CMD ["python", "./server/app.py"]