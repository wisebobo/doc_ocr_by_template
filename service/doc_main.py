# -*- coding:utf-8 -*-
import logging
from multiprocessing import Pool
from operator import itemgetter
from collections import OrderedDict
from service.doc_etl import doc_etl
from service.api.tencent_ai import tencent_ai
from service.api.baidu_ai import baidu_ai
from service.api.jd_ai import jd_ai
from service.api.faceplusplus_ai import faceplusplus_ai
from service.api.netease_ai import netease_ai
from settings import FACEPLUSPLUS_TEMPLATE
from util.readImage import readImage
from util.text_connector import TextConnector
from templates.loadTemplate import ocrTemplate

class doc_main(object):

    def __init__(self, pil_img, docType):
        self._img = pil_img
        self._img_grey = pil_img.convert('L')
        self._docType = docType

    def __nullRslt(self):
        __nullDict = {}
        __nullDict['valid_score'] = 0
        __nullDict['doc_type'] = self._docType
        return __nullDict

    def _getOcrResult(self, vendor, img):
        ocrBoxes = []

        if vendor == 'Baidu':
            tmpImg = readImage(img, outFormat='Bytes')
            __ai = baidu_ai()
            __rslt = __ai.ocr_general(tmpImg)

            if 'words_result_num' in __rslt.keys():
                if __rslt['words_result_num'] > 0:
                    for box in __rslt['words_result']:
                        if box['words']:
                            ocrBoxes.append([int(box['location']['left']), int(box['location']['top']), int(box['location']['width']), int(box['location']['height']), box['words']])

        elif vendor == 'Tencent':
            tmpImg = readImage(img, outFormat='Base64')
            __ai = tencent_ai()
            __ret, __rslt = __ai.ocr_generalocr(tmpImg)

            if __ret == 0:
                for box in __rslt['data']['item_list']:
                    if box['itemstring']:
                        ocrBoxes.append([int(box['itemcoord'][0]['x']), int(box['itemcoord'][0]['y']), int(box['itemcoord'][0]['width']), int(box['itemcoord'][0]['height']), box['itemstring']])

        elif vendor == 'JD':
            tmpImg = readImage(img, outFormat='Base64')
            __ai = jd_ai()
            __ret, __rslt = __ai.ocr_generalocr_v2(tmpImg)

            if 'result' in __rslt.keys():
                if __rslt['result']['code'] == 0:
                    for box in __rslt['result']['resultData']:
                        if box['text']:
                            ocrBoxes.append([int(box['location']['x']), int(box['location']['y']), int(box['location']['width']), int(box['location']['height']), box['text']])

        elif vendor == 'Face++':
            tmpImg = readImage(img, outFormat='Base64')
            __ai = faceplusplus_ai()
            __rslt = __ai.recognizeText(imgBase64=tmpImg)

            if __rslt['status'] == 'success':
                for box in __rslt['result']:
                    _tmp_X1 = box['child-objects'][0]['position'][0]['x']
                    _tmp_Y1 = box['child-objects'][0]['position'][0]['y']
                    _tmp_X2 = box['child-objects'][-1]['position'][2]['x']
                    _tmp_Y2 = box['child-objects'][-1]['position'][2]['y']

                    ocrBoxes.append([int(_tmp_X1), int(_tmp_Y1), int(_tmp_X2 - _tmp_X1), int(_tmp_Y2 - _tmp_Y1), box['value']])

        elif vendor == 'Face++_Template':
            if str(self._docType) in FACEPLUSPLUS_TEMPLATE.keys():
                tmpImg = readImage(img, outFormat='Base64')
                __ai = faceplusplus_ai()
                __rslt = __ai.OCRTemplate(templateID=FACEPLUSPLUS_TEMPLATE[str(self._docType)], imgBase64=tmpImg)

                if __rslt['status'] == 'success':
                    for box in __rslt['result']:
                        ocrBoxes.append([box['key'], ''.join(box['value']['text'])])

        elif vendor == 'Netease':
            tmpImg = readImage(img, outFormat='Base64')
            __ai = netease_ai()
            __rslt = __ai.ocr_generalocr(tmpImg)

            if __rslt['status'] == '000000':
                for box in __rslt['detail']['ocr']:
                    _position = box['position'].split(",")
                    _tmp_X1 = int(float(_position[0]))
                    _tmp_Y1 = int(float(_position[1]))
                    _tmp_X2 = int(float(_position[2]))
                    _tmp_Y2 = int(float(_position[3]))

                    ocrBoxes.append([_tmp_X1, _tmp_Y1, _tmp_X2 - _tmp_X1, _tmp_Y2 - _tmp_Y1, box['recognition']])

        ocrBoxes = sorted(ocrBoxes, key=itemgetter(1, 0))

        logging.info(vendor + ' OCR Boxes = ' + str(ocrBoxes))

        return ocrBoxes


    def _matchTemplate(self, vendor):

        ocr_rslt = self._getOcrResult(vendor, self._img)

        if vendor in ['Face++_Template']:
            result = OrderedDict()
            for box in ocr_rslt:
                result[box[0]] = box[1]
        else:
            if self._docType in [0, 5, 6]:
                result = []

                for box in ocr_rslt:
                    result.append(box[4])

            else:
                result = OrderedDict()
                if self._docType in [2, 3]:
                    _docType = self._docType + 0.1
                    for index, item in enumerate(ocr_rslt):
                        if ('PERMANENT' in item[4] or '永' in item[4] or '久' in item[4] or '性' in item[4]) and index < 3:
                            _docType = self._docType
                            break
                else:
                    _docType = self._docType

                _ocrTemplate = ocrTemplate(jsonFile=r'templates/template.json', docType=_docType)

                newImg, newRecogBoxes = _ocrTemplate.recog(self._img, ocr_rslt)

                if newImg:
                    ocrBoxes = self._getOcrResult(vendor, newImg)

                    if len(ocrBoxes):
                        _textConnector = TextConnector()
                        newOcrBoxes = _textConnector.connect_text(ocrBoxes, self._img.size, MAX_HORIZONTAL_GAP = 500)
                        newOcrBoxes = sorted(newOcrBoxes, key=itemgetter(1, 0))

                        for idx, recogBox in enumerate(newRecogBoxes):
                            fieldName = recogBox[4]
                            fieldType = recogBox[5]

                            fieldValue = ''
                            for box in newOcrBoxes:
                                if box[1] >= recogBox[1] and box[1] <= recogBox[1] + recogBox[3]:
                                    fieldValue = fieldValue + str(box[4])

                            result[fieldName] = fieldValue

        logging.info(vendor + ' Template result = ' + str(result))

        __ocr_rslt = doc_etl(self._img, vendor, result, self._docType)

        return __ocr_rslt

    def recogDoc(self):
        try:

            __pool = Pool(processes=5)

            tencent_ocr_rslt = __pool.apply_async(self._matchTemplate, ('Tencent',))
            baidu_ocr_rslt = __pool.apply_async(self._matchTemplate, ('Baidu',))
            jd_ocr_rslt = __pool.apply_async(self._matchTemplate, ('JD',))
            faceplusplus_ocr_rslt = __pool.apply_async(self._matchTemplate, ('Face++_Template',))
            netease_ocr_rslt = __pool.apply_async(self._matchTemplate, ('Netease',))

            __pool.close()

            try:
                tencent_rslt = tencent_ocr_rslt.get(timeout=5).to_dict()
            except Exception as e:
                tencent_rslt = {}
                tencent_rslt['valid_score'] = 0
                tencent_rslt['vendor'] = 'Tencent'
                logging.error('Error when running Tencent OCR : ' + str(e))
                __pool.terminate()

            try:
                baidu_rslt = baidu_ocr_rslt.get(timeout=5).to_dict()
            except Exception as e:
                baidu_rslt = {}
                baidu_rslt['valid_score'] = 0
                baidu_rslt['vendor'] = 'Baidu'
                logging.error('Error when running Baidu OCR : ' + str(e))
                __pool.terminate()

            try:
                jd_rslt = jd_ocr_rslt.get(timeout=5).to_dict()
            except Exception as e:
                jd_rslt = {}
                jd_rslt['valid_score'] = 0
                jd_rslt['vendor'] = 'JD'
                logging.error('Error when running JD OCR : ' + str(e))
                __pool.terminate()

            try:
                faceplusplus_rslt = faceplusplus_ocr_rslt.get(timeout=5).to_dict()
            except Exception as e:
                faceplusplus_rslt = {}
                faceplusplus_rslt['valid_score'] = 0
                faceplusplus_rslt['vendor'] = 'Face++'
                logging.error('Error when running Face++ OCR : ' + str(e))
                __pool.terminate()

            try:
                netease_rslt = netease_ocr_rslt.get(timeout=5).to_dict()
            except Exception as e:
                netease_rslt = {}
                netease_rslt['valid_score'] = 0
                netease_rslt['vendor'] = 'Netease'
                logging.error('Error when running Netease OCR : ' + str(e))
                __pool.terminate()

            __pool.join()

            rslt_dict = []
            rslt_dict.append([tencent_rslt['valid_score'], 5, tencent_rslt])
            rslt_dict.append([faceplusplus_rslt['valid_score'], 4, faceplusplus_rslt])
            rslt_dict.append([netease_rslt['valid_score'], 3, netease_rslt])
            rslt_dict.append([jd_rslt['valid_score'], 2, jd_rslt])
            rslt_dict.append([baidu_rslt['valid_score'],1, baidu_rslt])

            rslt_dict = sorted(rslt_dict, key=itemgetter(0, 1), reverse=True)


            logging.info('\nTencent result = ' + str(tencent_rslt))
            logging.info('\nBaidu result = ' + str(baidu_rslt))
            logging.info('\nJD result = ' + str(jd_rslt))
            logging.info('\nFace++ result = ' + str(faceplusplus_rslt))
            logging.info('\nNetease result = ' + str(netease_rslt))

            for i, rslt in enumerate(rslt_dict):
                logging.info('%2d - %-20s\t%f' % (i, rslt[2]['vendor'], rslt[0]))


            if rslt_dict[0][0] >= 60:
                return rslt_dict[0][2]
            else:
                return self.__nullRslt()

        except Exception as e:
            logging.error(str(e))
            return self.__nullRslt()
