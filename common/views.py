from django.db import connections
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from pymysql.cursors import DictCursor

from common.captcha import Captcha
from common.utils import gen_captcha_text


def captcha(request):
    """获取图片验证码"""
    code = gen_captcha_text()
    request.session['code'] = code
    image_bytes = Captcha.instance().generate(code)
    return HttpResponse(image_bytes, content_type='image/png')


def get_charts_data(request):
    """获取统计图表JSON数据"""
    # 在使用ORM框架时可以使用对象管理器的aggregate()和annotate()方法实现分组和聚合函数查询
    names = []
    totals = []
    with connections['backend'].cursor() as cursor:
        cursor.execute('select dname, total from vw_dept_emp')
        for row in cursor.fetchall():
            names.append(row[0])
            totals.append(row[1])
    return JsonResponse({'names': names, 'totals': totals})


def charts(request):
    return render(request, 'charts.html', {})
