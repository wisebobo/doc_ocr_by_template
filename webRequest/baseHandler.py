# -*- coding:utf-8 -*-
from tornado.web import RequestHandler, HTTPError
import settings
import json, logging
from util.signature import signature
from util.imageDeskew import imageDeskew

status_0 = dict(status_code=405, reason='Method not allowed.')


class baseHandler(RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, application, request, **kwargs):
        RequestHandler.__init__(self, application, request, **kwargs)
        self._sign = signature()
        self._deskew = imageDeskew()

    def set_default_headers(self):
        for key, value in settings.HTTP_HEADERS.items():
            self.set_header(key, value)

    def get(self, *args, **kwargs):
        raise HTTPError(**status_0)

    def post(self, *args, **kwargs):
        raise HTTPError(**status_0)

    def put(self, *args, **kwargs):
        raise HTTPError(**status_0)

    def delete(self, *args, **kwargs):
        raise HTTPError(**status_0)

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    def write_json(self, data, ret=0, msg=''):
        if msg:
            logging.error(str(msg))

        self.finish(json.dumps({
            'ret': ret,
            'msg': msg,
            'data': data
        }))

    def verify_sign(self):
        reqData = json.loads(self.request.body)

        return self._sign._verify(reqData)
