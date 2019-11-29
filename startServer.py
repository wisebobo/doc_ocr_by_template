# -*- coding:utf-8 -*-

import logging
from functools import partial
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from util import log
from webRequest.docOcrTaskHandler import docOcrTaskHandler
from webRequest.docTypeHandler import docTypeHandler

log.init_log('./log/app')
log.init_log('./log/access', logging.getLogger("tornado.access"))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/v1/doc", docOcrTaskHandler),
            (r"/v1/docType", docTypeHandler)
        ]
        settings = dict(
            autoescape=None,
            compress_whitespace=False,
            autoreload=False,
            debug=False,
            decompress_request=True,
            compress_response=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8089)
    tornado.ioloop.IOLoop.instance().start()
    print("Server is up and running ...")
