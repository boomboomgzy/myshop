import time
import os
from collections import OrderedDict
from django.conf import settings
from myshop.utils.goods import get_categories
from myshop.apps.contents.models import ContentCategory
from myshop.utils.constants import HtmlTemplate
from django.shortcuts import loader

def generate_static_index_html():
    """
    生成静态主页html文件
    """
    print('{}:生成静态主页文件'.format(time.ctime()))
    
    categorys=get_categories()
    
    contents=OrderedDict()
    content_categories=ContentCategory.objects.all()
    
    for cat in content_categories:
        contents[cat.keys]=cat.contents.filter(status=True).order_by('sequence')
        
    context={
        'categories':categorys,
        'contents':contents
    }
    template=loader.get_template(HtmlTemplate.INDEX_HTML)
    
    html_text=template.render()
    
    index_file_path=os.path.join(settings.STATICFILES_DIRS[0],HtmlTemplate.INDEX_HTML)
    
    with open(index_file_path,'w',encoding='utf-8') as f:
        f.write(html_text)