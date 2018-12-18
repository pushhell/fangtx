

# Django中的中间件其实更准确的名字应该称为拦截过滤器
# 拦截请求和响应为原有的业务逻辑动态添加横切关注功能
import re

from django.core.cache import caches
from django.http import JsonResponse


def block_sms_middleware(get_resp):

    def middleware(request, *args, **kwargs):
        path = request.path
        if path.startswith('/api/mobile_code/'):
            # 使用正则表达式的命名捕获组来获取URL路径中的手机号
            pattern = re.compile(r'/api/mobile_code/(?P<tel>1[3-9]\d{9})')
            matcher = pattern.match(path)
            if matcher:
                tel = matcher.group('tel')
                if caches['api'].get(tel):
                    return JsonResponse({'code': 20002, 'message': '请不要在120秒内重复发送手机验证码'})
            else:
                return JsonResponse({'code': 20001, 'message': '请输入有效的手机号'})
        # 前面的代码是对请求的过滤（在执行视图函数之前执行）
        resp = get_resp(request, *args, **kwargs)
        # 后面的代码是对响应的过滤（在执行视图函数之后执行）
        return resp

    return middleware
