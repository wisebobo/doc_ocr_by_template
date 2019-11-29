# -*- coding:utf-8 -*-

from urllib import request, parse, error
from PIL import Image
import json, base64, sys

sys.path.append("../../")
import settings
from util.readImage import readImage
from util.log import logging_elapsed_time

class faceplusplus_ai():
    """
        Face++ API
    """
    __API_Key = settings.FACEPLUSPLUS_API_Key

    __API_Secret = settings.FACEPLUSPLUS_API_Secret

    __detectUrl = 'https://api-cn.faceplusplus.com/facepp/v3/detect'

    __compareUrl = 'https://api-cn.faceplusplus.com/facepp/v3/compare'

    __searchUrl = 'https://api-cn.faceplusplus.com/facepp/v3/search'

    __facesetCreateUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/create'

    __facesetAddFaceUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/addface'

    __facesetRemoveFaceUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/removeface'

    __facesetUpdateUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/update'

    __facesetGetDetailUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/getdetail'

    __facesetDeleteUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/delete'

    __facesetGetFaceSetsUrl = 'https://api-cn.faceplusplus.com/facepp/v3/faceset/getfacesets'

    __faceAnalyzeUrl = 'https://api-cn.faceplusplus.com/facepp/v3/face/analyze'

    __faceGetDetailUrl = 'https://api-cn.faceplusplus.com/facepp/v3/face/getdetail'

    __faceSetUserIdUrl = 'https://api-cn.faceplusplus.com/facepp/v3/face/setuserid'

    __ocrBankCard = 'https://api-cn.faceplusplus.com/cardpp/v1/ocrbankcard'

    __ocrTemplate = 'https://api-cn.faceplusplus.com/cardpp/v1/templateocr'

    __recognizeText = 'https://api-cn.faceplusplus.com/imagepp/v1/recognizetext'

    def _get_img_content(self, imgPath):
        with open(imgPath, 'rb') as fp:
            return base64.b64encode(fp.read())

    def _format_rslt(self, rslt_flag, rslt_str):
        rslt = {}
        json_rslt = json.loads(rslt_str)

        if rslt_flag:
            rslt['status'] = 'success'
            rslt = dict(rslt, **json_rslt)
        else:
            rslt['status'] = 'fail'
            rslt['error_message'] = json_rslt['error_message']

        return rslt

    def _request(self, url, data, headers=None):
        """
            self._request('', {})
        """
        headers = {
            "Content-Type": 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0',
        }
        MyData = {}
        MyData['api_key'] = self.__API_Key
        MyData['api_secret'] = self.__API_Secret
        MyData.update(data)
        postdata = parse.urlencode(MyData)
        postdata = postdata.encode('utf-8')

        req = request.Request(url=url, data=postdata, headers=headers, method="POST")

        while True:
            try:
                res = request.urlopen(req)
                rslt = res.read().decode('utf-8')
                rslt = self._format_rslt(True, rslt)
                # print(rslt)
                break
            except error.URLError as e:
                rslt = e.read().decode('utf-8')
                rslt = self._format_rslt(False, rslt)
                # print(rslt)
                if rslt['error_message'] != 'CONCURRENCY_LIMIT_EXCEEDED':
                    break

        return rslt

    def detect(self, imgPath, options=None):
        """
            传入图片进行人脸检测和人脸分析。
            可以检测图片内的所有人脸，对于每个检测出的人脸，会给出其唯一标识 face_token，可用于后续的人脸分析、人脸比对等操作。对于正式 API Key，支持指定图片的某一区域进行人脸检测。
            本 API 支持对检测到的人脸直接进行分析，获得人脸的关键点和各类属性信息。对于试用 API Key，最多只对人脸框面积最大的 5 个人脸进行分析，其他检测到的人脸可以使用 Face Analyze API 进行分析。对于正式 API Key，支持分析所有检测到的人脸。
        """
        options = options or {}
        data = {}

        data['image_base64'] = self._get_img_content(imgPath)

        data = dict(data, **options)

        return self._request(self.__detectUrl, data)

    def compare_by_token(self, face_token1, face_token2, options=None):
        """
            将两个人脸进行比对，来判断是否为同一个人，返回比对结果置信度和不同误识率下的阈值。
            支持传入图片或 face_token 进行比对。使用图片时会自动选取图片中检测到人脸尺寸最大的一个人脸。
        """
        options = options or {}
        data = {}

        data['face_token1'] = face_token1  # 第一个人脸标识 face_token
        data['face_token2'] = face_token2  # 第二个人脸标识 face_token

        data = dict(data, **options)

        return self._request(self.__compareUrl, data)

    def compare_by_img(self, imgPath_1, imgPath_2, options=None):
        """
            将两个人脸进行比对，来判断是否为同一个人，返回比对结果置信度和不同误识率下的阈值。
            支持传入图片或 face_token 进行比对。使用图片时会自动选取图片中检测到人脸尺寸最大的一个人脸。
        """
        options = options or {}
        data = {}

        data['image_base64_1'] = self._get_img_content(imgPath_1)  # 第一个人脸base64 编码的二进制图片数据
        data['image_base64_2'] = self._get_img_content(imgPath_2)  # 第二个人脸base64 编码的二进制图片数据

        data = dict(data, **options)

        return self._request(self.__compareUrl, data)

    def search_by_img(self, imgPath, faceset_outer_id, options=None):
        """
            在一个已有的 FaceSet 中找出与目标人脸最相似的一张或多张人脸，返回置信度和不同误识率下的阈值。
            支持传入图片或 face_token 进行人脸搜索。使用图片进行搜索时会选取图片中检测到人脸尺寸最大的一个人脸。
        """
        options = options or {}
        data = {}

        data['image_base64'] = self._get_img_content(imgPath)  # base64 编码的二进制图片数据
        data['outer_id'] = faceset_outer_id  # 用户自定义的 FaceSet 标识

        data = dict(data, **options)

        return self._request(self.__searchUrl, data)

    def search_by_token(self, face_token, faceset_outer_id, options=None):
        """
            在一个已有的 FaceSet 中找出与目标人脸最相似的一张或多张人脸，返回置信度和不同误识率下的阈值。
            支持传入图片或 face_token 进行人脸搜索。使用图片进行搜索时会选取图片中检测到人脸尺寸最大的一个人脸。
        """
        options = options or {}
        data = {}

        data['face_token'] = face_token  # 进行搜索的目标人脸的 face_token
        data['outer_id'] = faceset_outer_id  # 用户自定义的 FaceSet 标识

        data = dict(data, **options)

        return self._request(self.__searchUrl, data)

    def facesetCreate(self, display_name, outer_id, options=None):
        """
            创建一个人脸的集合 FaceSet，用于存储人脸标识 face_token。一个 FaceSet 能够存储 10,000 个 face_token。
        """
        options = options or {}
        data = {}

        data['display_name'] = display_name  # 人脸集合的名字，最长256个字符，不能包括字符^@,&=*'"
        data['outer_id'] = outer_id  # 账号下全局唯一的 FaceSet 自定义标识，可以用来管理 FaceSet 对象。最长255个字符，不能包括字符^@,&=*'"

        data = dict(data, **options)

        return self._request(self.__facesetCreateUrl, data)

    def facesetAddFace(self, outer_id, face_tokens, options=None):
        """
            为一个已经创建的 FaceSet 添加人脸标识 face_token。一个 FaceSet 最多存储10,000个 face_token。
        """
        options = options or {}
        data = {}

        data['outer_id'] = outer_id  # 用户提供的 FaceSet 标识
        data['face_tokens'] = face_tokens  # 人脸标识 face_token 组成的字符串，可以是一个或者多个，用逗号分隔。最多不超过5个face_token

        data = dict(data, **options)

        return self._request(self.__facesetAddFaceUrl, data)

    def facesetRemoveFace(self, outer_id, face_tokens, options=None):
        """
            移除一个FaceSet中的某些或者全部face_token
        """
        options = options or {}
        data = {}

        data['outer_id'] = outer_id  # 用户提供的 FaceSet 标识
        data['face_tokens'] = face_tokens  # 需要移除的人脸标识字符串，可以是一个或者多个face_token组成，用逗号分隔。

        data = dict(data, **options)

        return self._request(self.__facesetRemoveFaceUrl, data)

    def facesetUpdate(self, outer_id, new_outer_id, display_name, options=None):
        """
            更新一个人脸集合的属性
        """
        options = options or {}
        data = {}

        data['outer_id'] = outer_id  # 用户自定义的FaceSet标识
        data['new_outer_id'] = new_outer_id  # 在api_key下全局唯一的FaceSet自定义标识，可以用来管理FaceSet对象。最长255个字符，不能包括字符^@,&=*'"
        data['display_name'] = display_name  # 人脸集合的名字，256个字符

        data = dict(data, **options)

        return self._request(self.__facesetUpdateUrl, data)

    def facesetGetDetail(self, outer_id, options=None):
        """
            获取一个 FaceSet 的所有信息，包括此 FaceSet 的 faceset_token, outer_id, display_name 的信息，以及此 FaceSet 中存放的 face_token 数量与列表。
        """
        options = options or {}
        data = {}

        data['outer_id'] = outer_id  # 用户自定义的FaceSet标识

        data = dict(data, **options)

        return self._request(self.__facesetGetDetailUrl, data)

    def facesetDeleteByID(self, outer_id, check_empty=1):
        """
            删除一个人脸集合。
        """
        data = {}

        data['outer_id'] = outer_id  # 用户自定义的FaceSet标识
        data[
            'check_empty'] = check_empty  # 删除时是否检查FaceSet中是否存在face_token，默认值为1.  0：不检查  1：检查  如果设置为1，当FaceSet中存在face_token则不能删除

        return self._request(self.__facesetDeleteUrl, data)

    def facesetDeleteByToken(self, faceset_token, check_empty=1):
        """
            删除一个人脸集合。
        """
        data = {}

        data['faceset_token'] = faceset_token  # FaceSet的标识
        data[
            'check_empty'] = check_empty  # 删除时是否检查FaceSet中是否存在face_token，默认值为1.  0：不检查  1：检查  如果设置为1，当FaceSet中存在face_token则不能删除

        return self._request(self.__facesetDeleteUrl, data)

    def facesetGetFaceSets(self, start=1, options=None):
        """
           获取某一 API Key 下的 FaceSet 列表及其 faceset_token、outer_id、display_name 和 tags 等信息。
        """
        options = options or {}
        data = {}

        data[
            'start'] = start  # 一个数字 n，表示开始返回的 faceset_token 在传入的 API Key 下的序号。 通过传入数字 n，可以控制本 API 从第 n 个 faceset_token 开始返回。返回的 faceset_token 按照创建时间排序。每次返回1000个FaceSets。

        data = dict(data, **options)

        return self._request(self.__facesetGetFaceSetsUrl, data)

    def faceAnalyze(self, face_tokens, options=None):
        """
            传入在 Detect API 检测出的人脸标识 face_token，分析得出人脸关键点，人脸属性信息。一次调用最多支持分析 5 个人脸。
        """
        options = options or {}
        data = {}

        data['face_tokens'] = face_tokens  # 一个字符串，由一个或多个人脸标识组成，用逗号分隔。最多支持 5 个 face_token。

        data = dict(data, **options)

        return self._request(self.__faceAnalyzeUrl, data)

    def faceGetDetail(self, face_token):
        """
            通过传入在Detect API检测出的人脸标识face_token，获取一个人脸的关联信息，包括源图片ID、归属的FaceSet。
        """
        data = {}

        data['face_token'] = face_token  # 人脸标识face_token

        return self._request(self.__faceGetDetailUrl, data)

    def faceSetUserId(self, face_token, user_id):
        """
            为检测出的某一个人脸添加标识信息，该信息会在Search接口结果中返回，用来确定用户身份。
        """
        data = {}

        data['face_token'] = face_token  # 人脸标识face_token
        data['user_id'] = user_id  # 用户自定义的user_id，不超过255个字符，不能包括^@,&=*'"  建议将同一个人的多个face_token设置同样的user_id。

        return self._request(self.__faceSetUserIdUrl, data)

    def OCRBankCard(self, imgPath=None, imgBase64=None):
        """
            检测和识别银行卡，并返回银行卡卡片边框坐标及识别出的银行卡号。当前 Beta 版本一次只支持识别一张银行卡，图像内有多张卡时，返回识别结果置信度最高的银行卡。支持任意角度的识别
        """
        data = {}

        if imgBase64:
            data['image_base64'] = imgBase64
        else:
            data['image_base64'] = self._get_img_content(imgPath)

        return self._request(self.__ocrBankCard, data)

    @logging_elapsed_time('Face++ OCR - recognizeText')
    def recognizeText(self, imgPath=None, imgBase64=None):
        """
            调用者提供图片文件或者图片URL，进行图片分析，找出图片中出现的文字信息
        """
        data = {}

        if imgBase64:
            data['image_base64'] = imgBase64
        else:
            data['image_base64'] = self._get_img_content(imgPath)

        __rslt = self._request(self.__recognizeText, data)

        return __rslt

    @logging_elapsed_time('Face++ OCR - OCRTemplate')
    def OCRTemplate(self, templateID, imgPath=None, imgBase64=None):
        """
            调用者提供图片文件或者图片URL，进行图片分析，找出图片中出现的文字信息
        """
        data = {}

        data['template_id'] = templateID

        if imgBase64:
            data['image_base64'] = imgBase64
        else:
            data['image_base64'] = self._get_img_content(imgPath)

        return self._request(self.__ocrTemplate, data)


if __name__ == "__main__":
    ai = faceplusplus_ai()

    _img = readImage(r"..\..\templates\Samples\04 - MACAU_ID_0021.jpg", outFormat='Base64')
    # rslt = ai.recognizeText(imgBase64=_img)
    rslt = ai.OCRTemplate(templateID=1573524413, imgBase64=_img)
    print(rslt)
