import os
from celery import Celery

#设置django配置文件
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE']='myshop.myshop.setting'

#celery实例
celery_app=Celery('myshop')

#加载配置文件
celery_app.config_from_object('celery_tasks.config')

#配置celery异步任务
task_packages=[
    'celery_tasks.sms',
    'celery_tasks.email',
]
celery_app.autodiscover_tasks(packages=task_packages)

