from signal import raise_signal
from typing import OrderedDict
from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
from myshop.utils.exceptions import BusinessException
from myshop.utils.enums import StatusCodeEnum
from myshop.apps.goods.models import SKU, GoodsCategory, GoodsChannel
from myshop.utils.goods import *
from myshop.utils.constants import GOODS_LIST_LIMIT, HtmlTemplate
import logging

from myshop.utils.result import R

logger=logging.getLogger(settings.LOGGER_NAME)


# Create your views here.

# /list/<category_id>/<page_num>
class ListView(View):
    
    
    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        # 判断category_id是否正确
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        # 接收sort参数：如果用户不传，就是默认的排序规则
        sort = request.GET.get('sort', 'default')

        # 查询商品频道分类
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 按照排序规则查询该分类商品SKU信息
        if sort == 'price':
            # 按照价格由低到高
            sort_field = 'sale_price'
        elif sort == 'hot':
            # 按照销量由高到低
            sort_field = '-sale_count'
        else:
            # 'price'和'sales'以外的所有排序方式都归为'default'
            sort = 'default'
            sort_field = 'create_time'
        skus = SKU.objects.filter(category=category, is_onsale=True).order_by(sort_field)

        # 创建分页器：每页N条记录
        paginator = Paginator(skus,GOODS_LIST_LIMIT)

        # 获取每页商品数据
        page_skus = paginator.page(page_num)

        # 获取列表页总页数
        total_page = paginator.num_pages

        # 渲染页面
        context = {
            'categories': categories,  # 频道分类
            'breadcrumb': breadcrumb,  # 面包屑导航
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        
        return render(request, HtmlTemplate.GOODS_LIST_HTML, context)
  
# /hot/<category_id>/
class HotGoodsView(View):
    
    def get(self,req,category_id):
        #根据销量排序商品数据
        skus=SKU.objects.filter(category_id=category_id,is_onsale=True).order_by('-sale_count')
        
        hot_skus=[]
        for sku in skus:
            hot_skus.append({
            'id': sku.id,
            'default_image_url': sku.default_image.url,
            'name': sku.name,
            'price': sku.sale_price,
        })
            
        res=R.ok().data(**{
            'hot_skus':hot_skus
        })
        
        return http.JsonResponse(res)
        
# /detail/<sku_id>
class DetailView(View):
    
    def get(self,req,sku_id):
        
        try:
            sku=SKU.objects.get(id=sku_id)
        except Exception as e:
            return render(req,HtmlTemplate.ERRORS_404_HTML)
        
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
        return render(req, HtmlTemplate.GOODS_DETAIL_HTML, context)
        
        
        
        
        
        
        
        
        
        