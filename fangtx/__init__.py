import os

import celery
import pymysql
from django.conf import settings

pymysql.install_as_MySQLdb()

# 注册环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fangtx.settings')

app = celery.Celery(
    'fangtx',
    broker='amqp://cuipeng:123456@59.110.223.164:5672/myhost1'
)

# 从默认的配置文件读取配置信息
app.config_from_object('django.conf:settings')

# Celery加载所有注册的应用
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
