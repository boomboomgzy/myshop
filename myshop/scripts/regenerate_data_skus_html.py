import sys
import os

#配置django环境
sys.path.append('G:\\vscode\webproject\myshop')
os.environ['DJANGO_SETTINGS_MODULE'] = 'myshop.settings'
import django
django.setup()
from django.template import loader
from django.conf import settings


from apps.goods.models import SKU
from myshop.utils.goods import get_breadcrumb,get_categories
from myshop.utils.constants import HtmlTemplate

def generate_html(sku_id):
    
        sku=SKU.objects.get(id=sku_id)
        
        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)

        # 获取当前商品的所有SKU
        skus = sku.goods.skus.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')

            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)

            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id

        # 获取当前商品的规格信息
        goods_specs = sku.goods.specs.order_by('id')

        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return None

        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        template = loader.get_template(HtmlTemplate.GOODS_DETAIL_HTML)
        html_text = template.render(context)
        file_path = os.path.join(settings.STATICFILES_DIRS[0], 'details/'+str(sku_id)+'.html')
        with open(file_path, 'w',encoding='utf-8') as f:
            f.write(html_text)
            
if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        generate_html(sku.id)