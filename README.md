Smartdrop
=========

Simple Flask-based HTTP server for dropping/getting your files in your shell using curl.

Usage
-----

Install dependencies:

`pip install -r dependencies.txt`

Run server:

`python server.py`

Drop file:

`curl -X POST -u admin:sciencek33psmewarm@night -F 'test=@/tmp/giphy.gif' 127.0.0.1:6664`

Get file:

`curl -X GET -u admin:sciencek33psmewarm@night 127.0.0.1:6664/file -o output_file`

Delete file:

`curl -X DELETE -u admin:sciencek33psmewarm@night 127.0.0.1:6664/file`
