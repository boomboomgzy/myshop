import sys
import os
from tabnanny import verbose
import django
from django.db import connection



sys.path.append('G:\\vscode\webproject\myshop')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myshop.settings")  # MB：项目名称
django.setup()

from myshop.apps.goods.models import SKU

skus=SKU.objects.all()
print(skus)
print(skus)
print(connection.queries)




