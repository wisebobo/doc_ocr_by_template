# -*- coding:utf-8 -*-
import hashlib
import urllib.request, urllib.error, urllib.parse
import base64
import json
import time
import requests
import logging
import sys, os

root_path = os.path.abspath("../../")
if root_path not in sys.path:
    sys.path.append(root_path)
root_path = os.path.abspath("../../../")
if root_path not in sys.path:
    sys.path.append(root_path)

import settings
from util.log import logging_elapsed_time


class tencent_ai(object):
    def __init__(self):
        self._app_id = settings.TENCENT_APP_ID
        self._app_key = settings.TENCENT_APP_KEY
        self.__client = requests
        self.__connectTimeout = 60.0
        self.__socketTimeout = 60.0
        self._proxies = {}

    def _readImage(self, filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    def _setParams(self, array, key, value):
        array[key] = value

    '''
    ======================================
    tencent获得参数对列表N（字典升级排序）
    ======================================
    1\依照算法第一步要求，对参数对进行排序，得到参数对列表N如下。
    参数名 	参数值
    app_id 	10000
    nonce_str 	20e3408a79
    text 	腾讯开放平台
    time_stamp 	1493449657

    2\按URL键值拼接字符串T
    依照算法第二步要求，将参数对列表N的参数对进行URL键值拼接，值使用URL编码，URL编码算法用大写字母，例如%E8，而不是小写%e8，得到字符串T如下：
    app_id=10000&nonce_str=20e3408a79&text=%E8%85%BE%E8%AE%AF%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0&time_stamp=1493449657

    3\拼接应用密钥，得到字符串S
    依照算法第三步要求，将应用密钥拼接到字符串T的尾末，得到字符串S如下。
    app_id=10000&nonce_str=20e3408a79&text=%E8%85%BE%E8%AE%AF%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0&time_stamp=1493449657&app_key=a95eceb1ac8c24ee28b70f7dbba912bf

    4\计算MD5摘要，得到签名字符串
    依照算法第四步要求，对字符串S进行MD5摘要计算得到签名字符串如。
    e8f6f347d549fe514f0c9c452c95da9d

    5\转化md5签名值大写
    对签名字符串所有字母进行大写转换，得到接口请求签名，结束算法。
    E8F6F347D549FE514F0C9C452C95DA9D

    6\最终请求数据
    在完成签名计算后，即可得到所有接口请求数据，进一步完成API的调用。
    text 	腾讯开放平台 	接口请求数据，UTF-8编码
    app_id 	10000 	应用标识
    time_stamp 	1493449657 	请求时间戳（秒级），用于防止请求重放
    nonce_str 	20e3408a79 	请求随机字符串，用于保证签名不可预测
    sign 	E8F6F347D549FE514F0C9C452C95DA9D 	请求签名
    '''

    def _genSignString(self, parser):
        uri_str = ''
        for key in sorted(parser.keys()):
            if key == 'app_key':
                continue
            value = urllib.parse.quote_plus(str(parser[key]), safe='')
            uri_str += "%s=%s&" % (key, value)
        sign_str = uri_str + 'app_key=' + parser['app_key']

        hash_md5 = hashlib.md5(sign_str.encode())
        return hash_md5.hexdigest().upper()

    def get_ret_msg(self, ret):

        ret_dict = {'0': 'Success',
                    '4096': r'Invalid parameters - 参数非法',
                    '12289': r'App does not exist - 应用不存在',
                    '12801': r'Material does not exist - 素材不存在',
                    '12802': r'Material ID not match with App ID - 素材ID与应用ID不匹配',
                    '16385': r'Lack of app_id parameter - 缺少app_id参数',
                    '16386': r'Lack of time_stamp parameter - 缺少time_stamp参数',
                    '16387': r'Lack of nonce_str parameter - 缺少nonce_str参数',
                    '16388': r'Invalid SIGN - 请求签名无效',
                    '16389': r'Lack of API authority - 缺失API权限',
                    '16390': r'Invalid time_stamp - 缺失API权限',
                    '16391': r'The result of synonym recognition is empty - 同义词识别结果为空',
                    '16392': r'Proper noun identification results are empty - 专有名词识别结果为空',
                    '16393': r'The result of the intention recognition is empty - 意图识别结果为空',
                    '16394': r'The result of gossip is empty - 闲聊返回结果为空',
                    '16396': r'Image format illegal - 图片格式非法',
                    '16397': r'The size of the picture is too large - 图片体积过大',
                    '16402': r'There is no face in the picture - 图片没有人脸',
                    '16403': r'Similarity error - 相似度错误',
                    '16404': r'Face detection failure - 人脸检测失败',
                    '16405': r'Image decoding failure - 图片解码失败',
                    '16406': r'Feature processing failure - 特征处理失败',
                    '16407': r'Extraction of outline error - 提取轮廓错误',
                    '16408': r'Extraction of gender error - 提取性别错误',
                    '16409': r'Extraction of facial expression error - 提取表情错误',
                    '16410': r'Extraction of age error - 提取年龄错误',
                    '16411': r'Extraction of attitude error - 提取姿态错误',
                    '16412': r'Extraction of glasses error - 提取眼镜错误',
                    '16413': r'Extraction of glamour error - 提取魅力值错误',
                    '16414': r'Speech synthesis failure - 语音合成失败',
                    '16415': r'The picture is empty - 图片为空',
                    '16416': r'Person already exist - 个体已存在',
                    '16417': r'Person does not exist - 个体不存在',
                    '16418': r'Face does not exist - 人脸不存在',
                    '16419': r'Face Group does not exist - 分组不存在',
                    '16420': r'Face Group list does not exist - 分组列表不存在',
                    '16421': r'Exceed the limit of maximum faces - 人脸个数超过限制',
                    '16422': r'Exceed the limit of maximum persons - 个体个数超过限制',
                    '16423': r'Exceed the limist of maximum groups - 组个数超过限制',
                    '16424': r'Adding nearly the same face to the same person - 对个体添加了几乎相同的人脸',
                    '16425': r'Unsupported image format - 无效的图片格式',
                    '16426': r'Image blur detection failure - 图片模糊度检测失败',
                    '16427': r'Gourmet picture detection failure - 美食图片检测失败',
                    '16428': r'Extraction of image fingerprint failure - 提取图像指纹失败',
                    '16429': r'Image feature comparison failure - 图像特征比对失败',
                    '16430': r'OCR photos are empty - OCR照片为空',
                    '16431': r'OCR recognition failure - OCR识别失败',
                    '16432': r'The input picture is not an ID card - 输入图片不是身份证',
                    '16433': r'There is not enough text for a business card - 名片无足够文本',
                    '16434': r'The business card text is too inclined - 名片文本行倾斜角度太大',
                    '16435': r'Business card is blurred - 名片模糊',
                    '16436': r'Business card name recognition failure - 名片姓名识别失败',
                    '16437': r'Business card phone recognition failure - 名片电话识别失败',
                    '16438': r'Image is a non business card image - 图像为非名片图像',
                    '16439': r'Detect or identify failure - 检测或者识别失败',
                    '16440': r'Cannot detect identify card - 未检测到身份证',
                    '16441': r'Please use second generation ID to scan - 请使用第二代身份证件进行扫描',
                    '16442': r'Not a positive photo of the ID card - 不是身份证正面照片',
                    '16443': r'Not the reverse photo of the ID card - 不是身份证反面照片',
                    '16444': r'Blurred document picture - 证件图片模糊',
                    '16445': r'Please avoid the direct light on the document surface - 请避开灯光直射在证件表面',
                    '16446': r'Driving license OCR identification failure - 行驾驶证OCR识别失败',
                    '16447': r'General OCR recognition failure - 通用OCR识别失败',
                    '16448': r'Bank card OCR preprocessing error - 银行卡OCR预处理错误',
                    '16449': r'Bank card OCR identification failure - 银行卡OCR识别失败',
                    '16450': r'Business license OCR preprocessing failure - 营业执照OCR预处理失败',
                    '16451': r'Business license OCR identifiation failure - 营业执照OCR识别失败',
                    '16452': r'Intention recognition timeout - 意图识别超时',
                    '16453': r'Gossip processing timeout - 闲聊处理超时',
                    '16454': r'Speech recognition decoding failure - 语音识别解码失败',
                    '16455': r'Long or empty voice - 语音过长或空',
                    '16456': r'Translation engine failure - 翻译引擎失败',
                    '16457': r'Unsupported translation types - 不支持的翻译类型',
                    '16460': r'The input picture does not match the recognition scene - 输入图片与识别场景不匹配',
                    '16461': r'The result of recognition is empty - 识别结果为空'}

        if str(ret) in ret_dict.keys():
            return ret_dict[str(ret)]
        else:
            return "Error code %s not defined!" % str(ret)

    def _invoke(self, url, params):
        self._url_data = urllib.parse.urlencode(params)
        headers = {
            # 伪装一个火狐浏览器
            "User-Agent": 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            "Content-Type": 'application/x-www-form-urlencoded'
        }

        try:
            response = self.__client.post(url, data=self._url_data.encode(),
                                          headers=headers, verify=True, timeout=(
                    self.__connectTimeout,
                    self.__socketTimeout,
                ), proxies=self._proxies
                                          )

            dict_rsp = json.loads(response.content.decode())
            if 'msg' in dict_rsp.keys():
                dict_rsp['msg'] = self.get_ret_msg(dict_rsp['ret'])
            return dict_rsp
        except Exception as e:
            dict_error = {}
            dict_error['ret'] = -1
            dict_error['msg'] = str(e)
            logging.error(str(e))
            return dict_error

    def rslt_to_dataTable(self, data, isMulti=False):
        _outList = []
        _tmpList = []
        if isMulti:
            for i in data.values():
                if isinstance(i, list):
                    for j in i:
                        _tmpList.append(str(j))
                        _outList.append(tuple(_tmpList))
                        _tmpList = []
        else:
            for i in data.values():
                if isinstance(i, str) or isinstance(i, int):
                    _tmpList.append(str(i))
                elif isinstance(i, dict):
                    _tmpList.append(",".join(str(x) for x in i.values()))
                elif isinstance(i, list):
                    _tmpList.append(",".join(str(x) for x in i))

            _outList.append(tuple(_tmpList))
        return _outList

    '''
    ======================================
    个体创建 - 创建一个个体（Person）
    ======================================
    获取一个个体（Person）的信息，包括ID，名字，备注，相关的人脸（Face）ID列表，以及所属组（Group）ID列表。
    '''

    @logging_elapsed_time('Tencent Face - New Person')
    def face_newperson(self, group_id, person_id, image, person_name, tag=None, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_newperson"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'group_ids', group_id)
        self._setParams(__data, 'person_id', person_id)
        self._setParams(__data, 'person_name', person_name)
        self._setParams(__data, 'image', image_data)
        if isinstance(tag, str):
            self._setParams(__data, 'tag', tag)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    删除个体 - 删除一个个体（Person）
    ======================================
    删除一个个体（Person）
    '''

    @logging_elapsed_time('Tencent Face - Delete Person')
    def face_delperson(self, person_id):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_delperson"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'person_id', person_id)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    增加人脸 - 将一组人脸（Face）加入到一个个体（Person）中
    ======================================
    将一组人脸（Face）加入到一个个体（Person）中。注意，一个人脸只能被加入到一个个体中。
    一个个体最多允许包含20个人脸；一次请求最多允许提交5个人脸，加入几乎相同的人脸会返回错误。
    多个人脸图片之间用“|”分隔
    '''

    @logging_elapsed_time('Tencent Face - Add Face')
    def face_addface(self, person_id, image, tag, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_addface"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'person_id', person_id)
        self._setParams(__data, 'images', image_data)
        self._setParams(__data, 'tag', tag)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    删除人脸 - 从一个个体（Person）中删除一组人脸（Face）
    ======================================
    删除一个个体（Person）下的人脸（Face），包括特征，属性和ID。
    （Face）ID 多个之间用“\“
    '''

    @logging_elapsed_time('Tencent Face - Delete Face')
    def face_delface(self, person_id, face_ids):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_delface"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'person_id', person_id)
        self._setParams(__data, 'face_ids', face_ids)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    设置信息 - 设置个体（Person）的名字或备注
    ======================================
    设置个体（Person）的名字或备注
    '''

    @logging_elapsed_time('Tencent Face - Set Person Info')
    def face_setinfo(self, person_id, person_name=None, tag=None):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_setinfo"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'person_id', person_id)
        if isinstance(person_name, str):
            self._setParams(__data, 'person_name', person_name)
        if isinstance(tag, str):
            self._setParams(__data, 'tag', tag)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    获取信息 - 获取一个个体（Person）的信息
    ======================================
    获取一个个体（Person）的信息，包括ID，名字，备注，相关的人脸（Face）ID列表，以及所属组（Group）ID列表。
    '''

    @logging_elapsed_time('Tencent Face - Get Person Info')
    def face_getinfo(self, person_id):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_getinfo"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'person_id', person_id)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    获取组列表 - 获取应用下所有的组（Group）ID列表
    ======================================
    获取一个AppId下所有Group ID
    '''

    @logging_elapsed_time('Tencent Face - Get Group Listing')
    def face_getgroupids(self):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_getgroupids"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    获取个体列表 - 获取一个组（Group）中的所有个体（Person）ID
    ======================================
    获取一个组（Group）中的所有个体（Person）ID
    '''

    @logging_elapsed_time('Tencent Face - Get Person List in a Group')
    def face_getpersonids(self, group_id):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_getpersonids"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'group_id', group_id)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    获取人脸列表 - 根据个体（Person）ID 获取人脸（Face）ID列表
    ======================================
    获取一个个体（Person）下所有人脸（Face）ID
    '''

    @logging_elapsed_time('Tencent Face - Get Face ID of a Person')
    def face_getfaceids(self, person_id):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_getfaceids"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'person_id', person_id)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    获取人脸信息 - 根据人脸（Face）ID 获取人脸（Face）信息
    ======================================
    获取一个人脸（Face）的详细信息
    '''

    @logging_elapsed_time('Tencent Face - Get Face Details')
    def face_getfaceinfo(self, face_id):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_getfaceinfo"
        __data = {}

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'face_id', face_id)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    人脸检测与分析 - 识别上传图像上面的人脸信息
    ======================================
    检测给定图片（Image）中的所有人脸（Face）的位置和相应的面部属性。位置包括（x, y, w, h），面部属性包括性别（gender）,
    年龄（age）, 表情（expression）, 魅力（beauty）, 眼镜（glass）和姿态（pitch，roll，yaw）。
    '''

    @logging_elapsed_time('Tencent Face - Detect Face')
    def face_detectface(self, image, mode=0, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_detectface"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        self._setParams(__data, 'mode', mode)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    多人脸检测 - 识别上传图像上面的人脸位置，支持多人脸识别。
    ======================================
    检测图片中的人脸位置，可以识别出一张图片上的多个人脸。
    '''

    @logging_elapsed_time('Tencent Face - Detect Multiple Faces')
    def face_detectmultiface(self, image, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_detectmultiface"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    人脸对比 - 对请求图片进行人脸对比
    ======================================
    对请求图片的两个人脸进行对比，计算相似性以及五官相似度。
    '''

    @logging_elapsed_time('Tencent Face - Compare Two Faces')
    def face_facecompare(self, image_a, image_b, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_facecompare"
        __data = {}

        if isBase64:
            image_data_a = image_a
            image_data_b = image_b
        else:
            image_data_a = self._readImage(image_a)
            image_data_a = base64.b64encode(image_data_a).decode()
            image_data_b = self._readImage(image_b)
            image_data_b = base64.b64encode(image_data_b).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image_a', image_data_a)
        self._setParams(__data, 'image_b', image_data_b)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    跨年龄人脸识别 - 上传两张人脸照，返回最相似的两张人脸及相似度。
    ======================================
    对比两张图片，并找出相似度最高的两张人脸；支持多人合照、两张图片中的人处于不同年龄段的情况。
    * 建议：source_image中的人脸尽量不超过10个，target_image中的人脸尽量不超过15个。*
    '''

    @logging_elapsed_time('Tencent Face - Compare Two Faces (Cross Age)')
    def face_detectcrossageface(self, image_a, image_b, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_detectcrossageface"
        __data = {}

        if isBase64:
            image_data_a = image_a
            image_data_b = image_b
        else:
            image_data_a = self._readImage(image_a)
            image_data_a = base64.b64encode(image_data_a).decode()
            image_data_b = self._readImage(image_b)
            image_data_b = base64.b64encode(image_data_b).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'source_image', image_data_a)
        self._setParams(__data, 'target_image', image_data_b)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    五官定位 - 对请求图片进行五官定位
    ======================================
    对请求图片进行五官定位，计算构成人脸轮廓的88个点，包括眉毛（左右各8点）、眼睛（左右各8点）、鼻子（13点）、嘴巴（22点）、脸型轮廓（21点）。
    '''

    @logging_elapsed_time('Tencent Face - Get Face Shape')
    def face_faceshape(self, image, mode=0, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_faceshape"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        self._setParams(__data, 'mode', mode)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    人脸识别 - 对请求图片中的人脸进行识别
    ======================================
    对于一个待识别的人脸图片，在一个组（Group）中识别出最相似的N个个体（Person）作为候选人返回，返回的N个个体（Person）按照相似度从大到小排列，N由参数topn指定。
    '''

    @logging_elapsed_time('Tencent Face - Find Person in a Group')
    def face_faceidentify(self, image, group_id, topn=5, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_faceidentify"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        self._setParams(__data, 'group_id', group_id)
        self._setParams(__data, 'topn', topn)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    人脸验证 - 对请求图片进行人脸验证
    ======================================
    根据提供的图片和个体（Person）ID，返回图片和个体是否是同一个人的判断以及置信度。
    '''

    @logging_elapsed_time('Tencent Face - Match a Person')
    def face_faceverify(self, image, person_id, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/face/face_faceverify"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        self._setParams(__data, 'person_id', person_id)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    身份证OCR识别 - 识别身份证图像上面的详细身份信息
    ======================================
    根据用户上传的包含身份证正反面照片，识别并且获取证件姓名、性别、民族、出生日期、地址、身份证号、证件有效期、发证机关等详细的身份证信息，并且可以返回精确剪裁对齐后的身份证正反面图片。
    card_type 身份证图片类型，0-正面，1-反面
    '''

    @logging_elapsed_time('Tencent OCR - ID Card')
    def ocr_idcardocr(self, image, card_type=0, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_idcardocr"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        self._setParams(__data, 'card_type', card_type)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    银行卡OCR识别 - 识别银行卡上面的字段信息
    ======================================
    根据用户上传的银行卡图像，返回识别出的银行卡字段信息。
    '''

    @logging_elapsed_time('Tencent OCR - Bank Card')
    def ocr_creditcardocr(self, image, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_creditcardocr"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    通用OCR识别 - 识别上传图像上面的字段信息
    ======================================
    根据用户上传的图像，返回识别出的字段信息。
    '''

    @logging_elapsed_time('Tencent OCR - General')
    def ocr_generalocr(self, image, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/ocr/ocr_generalocr"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    模糊图片检测 - 判断一个图像的模糊程度
    ======================================
    判断一个图像的模糊程度
    '''

    @logging_elapsed_time('Tencent Image - Fuzzy')
    def image_fuzzy(self, image, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/image/image_fuzzy"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt

    '''
    ======================================
    看图说话 - 用一句话描述图片
    ======================================
    用一句话文字描述图片
    '''

    @logging_elapsed_time('Tencent Vision - Image to Text')
    def vision_imgtotext(self, image, isBase64=True):
        __url = "https://api.ai.qq.com/fcgi-bin/vision/vision_imgtotext"
        __data = {}

        if isBase64:
            image_data = image
        else:
            image_data = self._readImage(image)
            image_data = base64.b64encode(image_data).decode()

        self._setParams(__data, 'app_id', self._app_id)
        self._setParams(__data, 'app_key', self._app_key)
        self._setParams(__data, 'time_stamp', int(time.time()))
        self._setParams(__data, 'nonce_str', int(time.time()))
        self._setParams(__data, 'image', image_data)
        self._setParams(__data, 'session_id', str(time.time()))
        sign_str = self._genSignString(__data)
        self._setParams(__data, 'sign', sign_str)
        __rslt = self._invoke(__url, __data)
        return __rslt['ret'], __rslt


if __name__ == "__main__":

    ai = tencent_ai()
    print(ai.ocr_generalocr(r"..\..\templates\Samples\001.jpg", isBase64=False))
