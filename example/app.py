"""
Usage:

    $ pip install wsgi-vmprof bottle
    $ python app.py &
    $ python
    >>> app.start()  # After that please access http://localhost:8080/ sometimes.
    >>> app.stop()
    <results are here...>
"""

import time

import bottle
from wsgi_vmprof import VmprofMiddleware

app = bottle.default_app()


@app.route('/')
def index():
    time.sleep(1)
    return "Hello world!!"

# Add wsgi-vmprof as a WSGI middleware!
app = VmprofMiddleware(app)

if __name__ == "__main__":
    bottle.run(app=app)
