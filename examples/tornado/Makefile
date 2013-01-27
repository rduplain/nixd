python := nixd/opt/python2.7/bin/python
wsdump := nixd/opt/python2.7/bin/wsdump.py

all: install

install:
	nixd/bin/nixd install

run: server

server: install
	@echo "Now run the client in another terminal: make client"
	$(python) server.py

client: install
	@echo "Ensure server is running: make server"
	@echo "This is a simple REPL-like interaction with server, using strings."
	$(wsdump) ws://localhost:8888/

clean:
	rm -f *.pyc
	rm -fr nixd/usr/ nixd/opt/ nixd/var/ nixd/src/

.SILENT: install
