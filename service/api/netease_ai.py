# -*- coding:utf-8 -*-
import requests, sys, hashlib, time, json, base64, logging
import urllib.parse
sys.path.append("../../")

import settings
from util.readImage import readImage
from util.log import logging_elapsed_time

class netease_ai(object):
    def __init__(self):
        self._app_id = settings.NETEASE_APP_ID
        self._app_key = settings.NETEASE_API_KEY
        self.__connectTimeout = 60.0
        self.__socketTimeout = 60.0
        self._proxies = {}

    def _setParams(self, array, key, value):
        array[key] = value

    def _genSignString(self, parser):
        uri_str = ''
        for key in sorted(parser.keys()):
            value = urllib.parse.quote_plus(str(parser[key]), safe='')
            uri_str += "%s=%s&" % (key, value)

        sign_str = uri_str + 'appkey=' + self._app_key

        hash_md5 = hashlib.md5(sign_str.encode())
        return hash_md5.hexdigest().upper()

    def _invoke(self, url, data, headers):
        try:
            _url_data = urllib.parse.urlencode(data)
            response = requests.post(url,
                                    data=_url_data.encode('utf-8'),
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
            '000000': 'Success',
            '000001': r'Invalid parameter - 参数错误',
            '000002': r'Business error - 业务错误',
            '000003': r'Request too frequently - 请求太频繁',
            '000004': r'Timeout - 请求超时',
            '000005': r'Busy service - 服务忙',
            '000006': r'Algorithm error - 算法运行出错',
            '000007': r'Image download error - 图片下载错误',
            '999999': r'Unknown error - 未知错误'
        }

        if str(ret) in ret_dict.keys():
            return ret_dict[str(ret)]
        else:
            return "Error code %s not defined!" % str(ret)

    @logging_elapsed_time('NETEASE OCR - General')
    def ocr_generalocr(self, imageBase64):
        __url = "http://ai.multimedia.netease.com/openaiplatform/ocr-service/ocr/detect"
        __params = {}

        timestamps = str(int(time.time()))

        self._setParams(__params, 'appId', self._app_id)
        self._setParams(__params, 'timestamp', timestamps)
        self._setParams(__params, 'nonce', timestamps)
        self._setParams(__params, 'image', imageBase64)
        self._setParams(__params, 'type', 'base64')

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
            'appId': self._app_id,
            'nonce': timestamps,
            'timestamp': timestamps,
            'sign': self._genSignString(__params)
        }

        __params.pop('appId')
        __params.pop('timestamp')
        __params.pop('nonce')

        __rslt = self._invoke(url=__url, data=__params, headers=headers)

        return __rslt


if __name__ == '__main__':
    ai = netease_ai()

    image_data = readImage(r"..\..\templates\Samples\14 - AU Driver - NSW.jpg", outFormat='Base64')
    print(ai.ocr_generalocr(image_data))
