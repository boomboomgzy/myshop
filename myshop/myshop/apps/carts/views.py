from itertools import count
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django_redis import get_redis_connection
from myshop.utils.constants import HtmlTemplate, Rediskey
from myshop.apps.goods.models import SKU
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.mixin import LoginRequiredJSONMixin
from django.conf import settings
import logging

logger=logging.getLogger(settings.LOGGER_NAME)

# /carts/
class CartsView(LoginRequiredJSONMixin,View):
    #购物车管理
    
    def get(self,req):
        #获取购物车信息
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        #得到redis中该用户的购物车信息  
        user_redis_cart_count_info=redis_cli.hgetall(Rediskey.USER_CARTS_COUNT_KEY.format(user_id=req.user.id))
        user_redis_cart_select_info=redis_cli.hgetall(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=req.user.id))
        #构造购物车信息数据
        cart_info_dic={}
        for sku_id,count in user_redis_cart_count_info.items():
            cart_info_dic[int(sku_id)]={
                'count':count.decode()
            }
        for sku_id,selected in user_redis_cart_select_info.items():
            cart_info_dic[int(sku_id)]['selected']=selected.decode()
        
        cart_skus=[]
        skus=SKU.objects.filter(id__in=cart_info_dic.keys())
        for sku in skus:
            cart_skus.append(
                    {
                        "id":sku.id,    
                        "name":sku.name,
                        "count":cart_info_dic[sku.id]["count"],
                        "selected":cart_info_dic[sku.id]["selected"],
                        "default_image_url":sku.default_image.url,
                        'stock':str(sku.stock),
                        "price":str(sku.sale_price),
                        "amount": str(int(cart_info_dic.get(sku.id).get("count")) * sku.sale_price)
                    }
                )
            
        
        res={
            "cart_skus":cart_skus,     
        }
        return render(req,HtmlTemplate.CART_LIST_HTML,res)

    def post(self,req):
        '''添加购物车
        '''
        json_dict=json.loads(req.body.decode())
        sku_id=json_dict.get('sku_id')
        count=json_dict.get('count')
        selected=json_dict.get('selected',True)
        
        if not all([sku_id,count]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        try:
            sku=SKU.objects.get(id=sku_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        try:
            count=int(count)
        except Exception as e:
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        if selected is not None:
            if not isinstance(selected,bool):
                raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        p1=redis_cli.pipeline()
        
        p1.hset(Rediskey.USER_CARTS_COUNT_KEY.format(user_id=req.user.id),sku_id,count)
        p1.hset(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=req.user.id),sku_id,str(selected))
        p1.execute()
        
        res=R.ok().data()
        
        return JsonResponse(res)
        
    def put(self,req):
        """修改购物车

        """
        
        json_dict=json.loads(req.body.decode())
        sku_id=json_dict.get('sku_id')
        count=json_dict.get('count')
        selected=json_dict.get('selected',True)
        
        if not all([sku_id,count]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        try:
            sku=SKU.objects.get(id=sku_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        try:
            count=int(count)
        except Exception as e:
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        if selected is not None:
            if not isinstance(selected,bool):
                raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        p1=redis_cli.pipeline()
        
        p1.hset(Rediskey.USER_CARTS_COUNT_KEY.format(user_id=req.user.id),sku_id,count)
        p1.hset(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=req.user.id),sku_id,str(selected))
        p1.execute()
        
        sku_info={
            'id':sku.id,
            'count':count,
            'selected':selected,
            'name':sku.name,
            'default_image_url':sku.default_image.url,
            'price':str(sku.sale_price),
            'amount':str(sku.sale_price*count),
            'stock':str(sku.stock)
        }
        
        res=R.ok().data(**{
            'cart_sku':sku_info
        })
        
        return JsonResponse(res)
    
    def delete(self,req):    
        #删除购物车记录
        json_body=json.loads(req.body.decode())
        sku_id=json_body.get('sku_id')
        
        try:
            sku=SKU.objects.get(id=sku_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        p1=redis_cli.pipeline()
        p1.hdel(Rediskey.USER_CARTS_COUNT_KEY.format(user_id=req.user.id),sku_id)
        p1.hdel(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=req.user.id),sku_id)
        p1.execute()
        res=R.ok().data()
        
        return JsonResponse(res)


# /carts/selection
class CartsSelectAllView(LoginRequiredJSONMixin,View):
    
    def put(self,req):    
        json_dict = json.loads(req.body.decode())
        selected = json_dict.get('selected', True)

        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        cart=redis_cli.hgetall(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=req.user.id))
        skus_id=cart.keys()
        for sku_id in skus_id:
            redis_cli.hset(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=req.user.id),sku_id,str(selected))
        
        res=R.ok().data()
        
        return JsonResponse(res)
        