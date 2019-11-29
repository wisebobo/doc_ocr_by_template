# -*- coding:utf-8 -*-
import json, logging, time
import tornado.web
import tornado.gen
import settings
from PIL import Image
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from webRequest.baseHandler import baseHandler
from service.doc_main import doc_main
from util.log import logging_elapsed_time
from util.readImage import readImage, captureFace
from model.classification.model import img_class_model

_docClass = img_class_model(config_file='model/classification/config.json',
                            # weight_file='model/classification/weights/weights-MobileNet-06.hdf5')
                            weight_file='model/classification/weights/weights-ResNet50-19.hdf5')

class docTypeHandler(baseHandler):
    executor = ThreadPoolExecutor(50)  # 起线程池，由当前RequestHandler持有

    # @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        logging.info('#####################################################################')
        logging.info('Document Type - Start : ' + time.asctime(time.localtime(time.time())))
        logging.info('#####################################################################')
        try:
            if self.request.headers.get("Content-Type") == "application/json":
                # logging.info(self.request.body)
                reqData = json.loads(self.request.body)

                signRslt = self.verify_sign()

                if signRslt['success']:
                    try:
                        imgBase64 = reqData['image']
                        api_id = reqData['api_id']

                        _docType, _confidence = yield self._docTypePredict(imgBase64)

                        _rslt = {}
                        _rslt['docType'] = _docType
                        _rslt['confidence'] = _confidence

                        self.write_json(data=_rslt)

                    except KeyError as e:
                        self.write_json(data={}, ret=10005, msg='Invalid JSON format, missing api_id/image')
                    except Exception as e:
                        self.write_json(data={}, ret=10002, msg=str(e))
                else:
                    self.write_json(data={}, ret=10003, msg=signRslt['msg'])
            else:
                self.write_json(data={}, ret=10004, msg='Content-Type need to be application/json')
        except Exception as e:
            self.write_json(data={}, ret=10005, msg=str(e))

    @run_on_executor
    def _docTypePredict(self, imgBase64):
        # Convert the base64 to PIL image
        __img = readImage(imgBase64, outFormat='PIL')
        __imgGrey = __img.convert('L')

        # Get Doc Type by running predict model
        docType, confidence = _docClass.predict(__imgGrey)

        return docType, confidence
