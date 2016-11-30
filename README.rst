===========
wsgi-vmprof
===========

**wsgi-vmprof** WSGI Middleware for integrating vmprof.

* https://github.com/vmprof/vmprof-python
* https://github.com/vmprof/vmprof-server

How to use
==========

Installation
------------

.. code-block:: console

   $ pip install wsgi-vmprof

Basic Usage
-----------

.. code-block:: python

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

Requirements
============

- Python 3.3 or later
- vmprof

License
=======

This software is licensed under the MIT License.
