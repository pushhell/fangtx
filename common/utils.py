"""
工具函数
"""
import http.client
import json
import logging
import random

from hashlib import md5
from io import StringIO
from urllib.error import URLError
from urllib.parse import urlencode

from fangtx import app


def get_ip_address(request):
    """获得请求的IP地址"""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    return ip or request.META['REMOTE_ADDR']


MD5_GEN_PROTO = md5()


def to_md5_hex(origin_str):
    """生成MD5摘要"""
    # 对原型模式（prototype pattern）的使用
    generator = MD5_GEN_PROTO.copy()
    generator.update(origin_str.encode('utf-8'))
    return generator.hexdigest()


def gen_mobile_code(length=6):
    """生成指定长度的手机验证码"""
    code = StringIO()
    for _ in range(length):
        code.write(str(random.randint(0, 9)))
    return code.getvalue()


ALL_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def gen_captcha_text(length=4):
    """生成指定长度的图片验证码文字"""
    code = StringIO()
    chars_len = len(ALL_CHARS)
    for _ in range(length):
        index = random.randrange(chars_len)
        code.write(ALL_CHARS[index])
    return code.getvalue()


SMS_SERVER = '106.ihuyi.com'
SMS_URL = '/webservice/sms.php?method=Submit'
SMS_ACCOUNT = 'C38434632'
SMS_PASSWORD = '621c711b9840d5e7a75143c3c3b5e23f'
MSG_TEMPLATE = '您的验证码是：%s。请不要把验证码泄露给其他人。'


@app.task
def send_short_message(tel, code):
    """发送短信"""
    params = urlencode({
        'account': SMS_ACCOUNT,
        'password': SMS_PASSWORD,
        'content': MSG_TEMPLATE % code,
        'mobile': tel,
        'format': 'json'
    })
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/plain'
    }
    conn = http.client.HTTPConnection(SMS_SERVER, port=80, timeout=10)
    try:
        conn.request('POST', SMS_URL, params, headers)
        json_str = conn.getresponse().read().decode('utf-8')
        return json.loads(json_str)
    except URLError or KeyError as e:
        logging.error(e)
        return json.dumps({
            'code': 500,
            'msg': '短信服务暂时无法使用'
        })
    finally:
        conn.close()
