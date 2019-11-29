# -*- coding:utf-8 -*-
import json, logging, time, requests
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
from util.signature import get_current_timestamp

class docOcrTaskHandler(baseHandler):
    executor = ThreadPoolExecutor(50)  # 起线程池，由当前RequestHandler持有

    # @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        logging.info('#####################################################################')
        logging.info('Document OCR - Start : ' + time.asctime(time.localtime(time.time())))
        logging.info('#####################################################################')
        try:
            if self.request.headers.get("Content-Type") == "application/json":

                reqData = json.loads(self.request.body)

                signRslt = self.verify_sign()

                if signRslt['success']:
                    try:
                        imgBase64 = reqData['image']
                        api_id = reqData['api_id']

                        _pil_img, _face_img, _docType, _confidence = yield self._imgETL(imgBase64)

                        ocr_rslt = yield self._runOcr(_pil_img, _docType, _confidence)

                        if ocr_rslt['valid_score'] == 0:
                            self.write_json(data=ocr_rslt, ret=10001, msg='Your documents do not meet the requirements! When photographing, you should reduce the inclination or side angle. Please re-take the document photo and try again!')
                        else:
                            if _face_img:
                                ocr_rslt['face'] = _face_img
                            else:
                                logging.info('Face not found')
                                ocr_rslt['face'] = ''

                            self.write_json(data=ocr_rslt)

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

    def _getDocType(self, imgBase64):
        params = {
            "api_id": "demo_id",
            "timestamp": get_current_timestamp(),
            "image": readImage(imgBase64, outFormat='Base64'),
            "sign": "123"
        }

        params['sign'] = self._sign._sign(params)
        url = 'http://127.0.0.1:8089/ghk_oci/v1/docType'

        headers = {'content-type': "application/json"}
        response = requests.post(url, data=json.dumps(params), headers=headers)
        __rslt = json.loads(response.content.decode())

        return __rslt['data']['docType'], __rslt['data']['confidence']

    @run_on_executor
    def _imgETL(self, imgBase64):
        # Convert the base64 to PIL image
        __img = readImage(imgBase64, outFormat='PIL')
        __img = __img.convert("RGB")

        # Resize the image to the given width
        (x, y) = __img.size

        if x < y:
            x_s = 600
            y_s = int(y * x_s / x)
        else:
            y_s = 600
            x_s = int(x * y_s / y)


        __img0 = __img.resize((x_s, y_s), Image.ANTIALIAS)

        # Image Skew handling
        angle = self._deskew.determine_skew(__img0)
        logging.info('Image angle = ' + str(angle))
        __img1 = self._deskew.deskew(__img0, angle)
        __imgGrey = __img1.convert('L')

        # Capture Face image
        __faceImg = captureFace(__img0)

        # Get Doc Type by running predict model
        docType, confidence = self._getDocType(__imgGrey)

        return __imgGrey, __faceImg, docType, confidence

    @run_on_executor
    def _runOcr(self, img, docType, confidence):
        ocr = doc_main(img, docType)
        ocr_rslt = ocr.recogDoc()

        if ocr_rslt['valid_score'] == 0 and confidence < 0.7:
            ocr = doc_main(img, 0)
            ocr_rslt = ocr.recogDoc()

        return ocr_rslt
