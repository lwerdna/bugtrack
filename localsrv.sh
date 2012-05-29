#!/bin/bash

if [[ $OSTYPE != darwin* ]]; then  # for non-Mac systems...
	thttpd -p 2048 -c "*.py"
else
	rm cgi-bin/*
	for f in *.py; do ln $f cgi-bin/$f; done
	python server.py
	rm cgi-bin/*
fi
