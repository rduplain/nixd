all: install

install:
	nixd/bin/nixd install

run: install
	nixd/opt/python2.7/bin/gunicorn -b 127.0.0.1:5000 -w 2 --access-logfile=- app:app

clean:
	rm -f *.pyc
	rm -fr nixd/usr/ nixd/opt/ nixd/var/ nixd/src/

.SILENT: install
