import os
from io import BytesIO
from urllib.parse import quote

import xlwt
from django.http import HttpResponse, StreamingHttpResponse

from backend.models import Emp, Dept


# 如果需要动态生成PDF文件可以考虑使用三方库ReportLab
def export_pdf(request):
    filename = 'Python网络数据采集.pdf'
    fullpath = os.path.join(os.path.dirname(__file__), 'resources', filename)
    # 如果需要导出的文件较大（占用内存较多）可以通过迭代的方式进行读取
    file_stream = open(fullpath, 'rb')
    file_iter = iter(lambda: file_stream.read(1024), b'')
    resp = StreamingHttpResponse(file_iter)
    # 指定MIME类型（告知浏览器返回的内容的类型）
    resp['content-type'] = 'application/pdf'
    # 将中文文件名处理成百分号编码
    filename = quote(filename)
    # 指定内容处置的方式（告知浏览器是内联显示还是下载文件）
    resp['content-disposition'] = f'attachment; filename="{filename}"'
    return resp


def get_style(name, color=0, bold=False, italic=False):
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.name = name
    font.colour_index = color
    font.bold = bold
    font.italic = italic
    style.font = font
    return style


# 如果要导出数据量非常大的报表 应该用计划任务（定时任务）提前导出成文件并保存到指定路径
# 当需要报表时只需要按照上面讲解的流式读取文件的方式读文件输出二进制数据到浏览器即可
def export_emp_excel(request):
    # 创建Excel工作簿
    workbook = xlwt.Workbook()
    # 向工作簿中添加工作表
    sheet = workbook.add_sheet('员工详细信息')
    # 设置表头
    titles = ['编号', '姓名', '主管', '职位', '工资', '部门名称']
    for col, title in enumerate(titles):
        sheet.write(0, col, title, get_style('HanziPenSC-W3', 2, True))
    # 使用Django的ORM框架查询员工数据
    # only() - 指定查询哪些属性 / defer() - 指定哪些属性要推迟查询
    # select_related() / prefetch_related() - 避免1+N查询问题（内连接、左外连接）
    emps = Emp.objects.all().select_related('dept').select_related('mgr')
    cols = ['no', 'name', 'mgr', 'job', 'sal', 'dept']
    # 通过二重循环将员工表的数据写入工作表的单元格
    for row, emp in enumerate(emps):
        for col, prop in enumerate(cols):
            val = getattr(emp, prop, '')
            if isinstance(val, (Dept, Emp)):
                val = val.name
            sheet.write(row + 1, col, val)
    # 将Excel文件的二进制数据写入内存
    buffer = BytesIO()
    workbook.save(buffer)
    # 通过HttpResponse对象向浏览器输出Excel文件
    resp = HttpResponse(buffer.getvalue())
    resp['content-type'] = 'application/msexcel'
    resp['content-disposition'] = 'attachment; filename="detail.xls"'
    return resp
