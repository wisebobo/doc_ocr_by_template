# -*- coding:utf-8 -*-
import json
from aip import AipOcr
from PIL import Image
import sys, os, base64

root_path = os.path.abspath("../../")
if root_path not in sys.path:
    sys.path.append(root_path)

import settings
from util.log import logging_elapsed_time
from util.readImage import readImage


class baidu_ai(object):
    def __init__(self):
        self.ocr = AipOcr(settings.BAIDU_APP_ID, settings.BAIDU_API_KEY, settings.BAIDU_SECRET_KEY)

    def load_json(self, rslt):
        json_dump = json.dumps(rslt, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=True)
        json_rslt = json.loads(json_dump)
        return json_rslt

    '''
    ======================================
    通用OCR识别 - 识别上传图像上面的字段信息
    ======================================
    根据用户上传的图像，返回识别出的字段信息。
    '''

    @logging_elapsed_time('Baidu OCR - Basic General')
    def ocr_basicGeneral(self, image):
        # 定义参数变量
        options = {
            'detect_direction': "true",
            'probability': "true",
        }

        # 调用人脸属性检测接口
        result = self.ocr.basicGeneral(image, options)
        json_rslt = self.load_json(result)
        return json_rslt

    '''
    ======================================
    通用文字识别（高精度版）- 用户向服务请求识别某张图中的所有文字，相对于通用文字识别该产品精度更高，但是识别耗时会稍长。
    ======================================
    根据用户上传的图像，返回识别出的字段信息。
    '''

    @logging_elapsed_time('Baidu OCR - Basic Accurate')
    def ocr_basicAccurate(self, image):
        # 定义参数变量
        options = {
            'detect_direction': "true",
            'probability': "true",
        }

        # 调用人脸属性检测接口
        result = self.ocr.basicAccurate(image, options)
        json_rslt = self.load_json(result)
        return json_rslt

    '''
    ======================================
    通用文字识别（含位置信息版）- 用户向服务请求识别某张图中的所有文字，并返回文字在图中的位置信息。
    ======================================
    根据用户上传的图像，返回识别出的字段信息。
    '''

    @logging_elapsed_time('Baidu OCR - General')
    def ocr_general(self, image):
        # 定义参数变量
        options = {
            'detect_direction': "true",
            'probability': "true",
            'detect_language': 'true',
            'recognize_granularity': 'small',
            'language_type': 'CHN_ENG'
        }

        result = self.ocr.general(image, options)
        json_rslt = self.load_json(result)
        return json_rslt


    '''
    ======================================
    身份证识别 - 用户向服务请求识别身份证，身份证识别包括正面和背面。
    ======================================
    '''

    @logging_elapsed_time('Baidu OCR - ID Card')
    def ocr_idcardocr(self, image, id_card_side='front'):
        # 定义参数变量
        options = {
            'detect_direction': "true",
            'detect_risk': "true",
        }

        # 调用人脸属性检测接口
        result = self.ocr.idcard(image, id_card_side, options)
        json_rslt = self.load_json(result)
        return json_rslt

    '''
    ======================================
    银行卡OCR识别 - 识别银行卡上面的字段信息
    ======================================
    '''

    @logging_elapsed_time('Baidu OCR - Bank Card')
    def ocr_creditcardocr(self, image):
        # 定义参数变量
        options = {}

        # 调用人脸属性检测接口
        result = self.ocr.bankcard(image, options)
        json_rslt = self.load_json(result)
        return json_rslt


if __name__ == '__main__':

    imgFile = r'..\..\templates\Samples\001.jpg'

    img = Image.open(imgFile)
    img = img.convert('RGB')
    imgBase64 = readImage(img, outFormat='Base64')

    __ai = baidu_ai()
    __rslt = __ai.ocr_general(base64.b64decode(imgBase64))

    print(__rslt)
