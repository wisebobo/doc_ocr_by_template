# -*- coding:utf-8 -*-
import requests, sys, hashlib, time, json, base64, logging

sys.path.append("../../")

import settings
from util.readImage import readImage
from util.log import logging_elapsed_time

class jd_ai(object):
    def __init__(self):
        self._app_id = settings.JD_APP_ID
        self._app_key = settings.JD_APP_KEY
        self.__connectTimeout = 60.0
        self.__socketTimeout = 60.0
        self._proxies = {}

    def _setParams(self, array, key, value):
        array[key] = value

    def _genSignString(self):
        timeStamp = int(time.time() * 1000)
        sign_str = self._app_key + str(timeStamp)
        hash_md5 = hashlib.md5(sign_str.encode())

        return timeStamp, hash_md5.hexdigest()

    def _invoke(self, url, params, data=None, headers=None):

        params['timestamp'], params['sign'] = self._genSignString()

        try:
            response = requests.post(url, params=params,
                                    data=data,
                                    headers=headers,
                                    verify=True,
                                    timeout=(self.__connectTimeout, self.__socketTimeout,),
                                    proxies=self._proxies)

            dict_rsp = json.loads(response.content.decode())

            return dict_rsp
        except Exception as e:
            dict_error = {}
            dict_error['ret'] = -1
            dict_error['msg'] = str(e)
            logging.error(str(e))
            return dict_error

    def get_ret_msg(self, ret):

        ret_dict = {
            '10000': 'Success',
            '10001': r'Incorrect appKey - 错误的请求appkey',
            '10003': r'不存在相应的数据信息',
            '10004': r'URL上appkey参数不能为空',
            '12001': r'Image does not exist - 图像不存在',
            '12002': r'Image format error - 图像格式错误',
            '12003': r'Image size error - 图像大小错误',
            '12004': r'Parameter does not exit - 参数不存在',
            '12005': r'Parameter value is null - 参数值为null',
            '13002': r'Timeout - 超时',
            '13004': r'No content recognition - 无内容识别',
            '13005': r'Internel error - 参数不存在'

        }

        if str(ret) in ret_dict.keys():
            return ret_dict[str(ret)]
        else:
            return "Error code %s not defined!" % str(ret)

    @logging_elapsed_time('JD OCR - General')
    def ocr_generalocr(self, imageBytes):
        __url = "https://aiapi.jd.com/jdai/ocr_universal"
        __params = {}

        headers = {
            'Content-Type': 'image/jpg'
        }

        self._setParams(__params, 'appkey', self._app_id)

        __rslt = self._invoke(url=__url, params=__params, data=imageBytes, headers=headers)

        return __rslt['code'], __rslt

    @logging_elapsed_time('JD OCR - General v2')
    def ocr_generalocr_v2(self, imageBase64):
        __url = "https://aiapi.jd.com/jdai/ocr_universal_v2"
        __params = {}

        headers = {
            'Content-Type': 'application/json'
        }

        data = {"imageBase64Str": imageBase64}

        self._setParams(__params, 'appkey', self._app_id)

        __rslt = self._invoke(url=__url, params=__params, data=json.dumps(data), headers=headers)

        return __rslt['code'], __rslt

if __name__ == '__main__':
    ai = jd_ai()

    image_data = readImage(r"..\..\templates\Samples\14 - AU Driver - NSW.jpg", outFormat='Bytes')
    print(ai.ocr_generalocr(image_data))

    image_data = readImage(r"..\..\templates\Samples\14 - AU Driver - NSW.jpg", outFormat='Base64')
    print(ai.ocr_generalocr_v2(image_data))
