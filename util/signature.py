# -*- coding:utf-8 -*-
import hashlib, time, datetime, logging

md5 = lambda pwd: hashlib.md5(pwd.encode()).hexdigest()
get_current_timestamp = lambda: int(time.mktime(datetime.datetime.now().timetuple()))


class signature(object):
    """ 接口签名认证 """

    def __init__(self):
        self._accessKeys = [
            {"api_id": "demo_id", "api_key": "demo_secret"},
        ]
        # 时间戳有效时长，单位秒
        self._timestamp_expiration = 600

    def _check_req_timestamp(self, req_timestamp):
        """ 校验时间戳
        @pram req_timestamp str,int: 请求参数中的时间戳(10位)
        """
        if len(str(req_timestamp)) == 10:
            req_timestamp = int(req_timestamp)
            now_timestamp = get_current_timestamp()
            if req_timestamp - self._timestamp_expiration <= now_timestamp and req_timestamp + self._timestamp_expiration >= now_timestamp:
                return True
        return False

    def _check_req_accesskey_id(self, req_accesskey_id):
        """ 校验accesskey_id
        @pram req_accesskey_id str: 请求参数中的用户标识id
        """
        if req_accesskey_id in [i['api_id'] for i in self._accessKeys if 'api_id' in i]:
            return True
        return False

    def _get_accesskey_secret(self, accesskey_id):
        """ 根据accesskey_id获取对应的accesskey_secret
        @pram accesskey_id str: 用户标识id
        """
        return [i['api_key'] for i in self._accessKeys if i.get('api_id') == accesskey_id][0]

    def _sign(self, parameters):
        """ MD5签名
        @param parameters dict: 除signature外请求的所有查询参数(公共参数和私有参数)
        """
        # Exclude "sign" from the signature process
        if "sign" in parameters:
            parameters.pop("sign")
        accesskey_id = parameters["api_id"]

        # NO.1 参数排序 Parameters Ordering
        sortedParameters = sorted(parameters.items(), key=lambda parameters: parameters[0])

        # NO.2 排序后拼接字符串 Concatenate the parameters to URL key pair format
        canonicalizedQueryString = ''
        for (k, v) in sortedParameters:
            canonicalizedQueryString += k + "=" + str(v) + "&"

        # No.3 Append the api_key
        canonicalizedQueryString += "api_key=" + self._get_accesskey_secret(accesskey_id)

        # NO.4 加密返回签名: MD5 and Upper case
        signature = md5(canonicalizedQueryString).upper()

        return signature

    def _verify(self, req_params):
        """ 校验请求是否有效
        @param req_params dict: 请求的所有查询参数(公共参数和私有参数)
        """
        res = dict(msg=None, success=False)
        try:
            req_timestamp = req_params["timestamp"]
            req_accesskey_id = req_params["api_id"]
            req_signature = req_params["sign"]
        except KeyError as e:
            res.update(msg="Invalid public params")
        except Exception as e:
            res.update(msg="Unknown server error")
        else:
            # NO.1 校验时间戳
            if self._check_req_timestamp(req_timestamp):
                # NO.2 校验accesskey_id
                if self._check_req_accesskey_id(req_accesskey_id):
                    # NO.3 校验签名
                    exp_signature = self._sign(req_params)
                    if req_signature == exp_signature:
                        res.update(msg="Verification pass", success=True)
                    else:
                        logging.error("Invalid Sign - Input: %s, Expected: %s" % (req_signature, exp_signature))
                        res.update(msg="Invalid sign")
                else:
                    res.update(msg="Invalid api_id")
            else:
                res.update(msg="Invalid timestamp")
        return res


if __name__ == "__main__":

    mySign = signature()
    params = {
        "api_id": "demo_id",
        "timestamp": get_current_timestamp(),
        "image": '123'
    }

    params['sign'] = mySign._sign(params)

    print(mySign._verify(params))
