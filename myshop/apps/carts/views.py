from asyncio.log import logger
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django_redis import get_redis_connection
from myshop.utils.constants import Rediskey
from myshop.apps.goods.models import SKU
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R


# /carts/
class CartsView(View):
    #购物车管理
    
    #REDIS 购物车数据示例
    #'USER_CARTS_KEY':{
    #    'sku.id':{
    #        'count':5,
    #        'selected':'True'  #True标识选中,False表示未选中
    #    }
    #} 
    
    def get(self,req):
        #获取购物车信息
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        #得到redis中该用户的购物车信息  
        user_redis_cart_info=redis_cli.hgetall(Rediskey.USER_CARTS_KEY.format(user_id=req.user.id))
        
        #构造购物车信息数据
        
        cart_info_dic={}
        skus=SKU.objects.in_bulk(list(user_redis_cart_info.keys()))
        for sku in skus:
            cart_info_dic[sku.id]={
                'name':sku.name,
                'count':user_redis_cart_info[sku.id]['count'],
                'selected':user_redis_cart_info[sku.id]['selected'],
                'default_image_url':sku.default_image_url,
                'price':str(sku.sale_price),
                'total_price': str(user_redis_cart_info[sku.id]['count'] * sku.sale_price)
            }
        
        res=R.ok().data(**{
            'cart_info':cart_info_dic       
        })
        return JsonResponse(res)

    def post(self,req):
        """加入或修改购物车

        """
        sku_id=req.POST.get('sku_id')
        count=req.POST.get('count')
        selected=req.POST.get('selected',True)
                
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
        
        if not isinstance(selected,bool):
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        p1=redis_cli.pipeline()
        
        p1.hset(Rediskey.USER_CARTS_KEY.format(user_id=req.user.id),sku_id,{
            'count':count,
            'selected':selected
        })
        
        p1.hget(Rediskey.USER_CARTS_KEY.format(user_id=req.user.id))
        
        neworupdated_sku=p1.execute()
       
        res=R.ok().data(neworupdated_sku)
        
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
        
        redis_cli=get_redis_connection(settings.CARTS_CHAHE_ALIAS)
        
        redis_cli.hdel(Rediskey.USER_CARTS_KEY.format(user_id=req.user.id),sku_id)
        
        res=R.ok().data()
        
        return JsonResponse(res)



