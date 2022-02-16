from email.headerregistry import Address
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from myshop.apps.goods.models import SKU
from myshop.apps.orders.models import Order, OrderSku
from django.conf import Settings, settings
import logging
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.constants import ORDER_STATUS, Rediskey
from django_redis import get_redis_connection
logger=logging.getLogger(Settings.LOGGER_NAME)

class OrderCommentView(View):

    
    def get(self,req):
        """ 返回未评论sku的数据

        Raises:
            BusinessException: order_id无效
        """
        order_id=req.GET.get('order_id')
        try:
            order=Order.objects.get(order_id=order_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        else:
            uncomment_order_skus=order.order_skus.filter(is_commented=False)
            uncomment_order_skus_list=[]
            for order_sku in uncomment_order_skus:
                uncomment_order_skus_list.append({
                    'order_sku_id':order_sku.sku.id,
                    'order_sku_name':order_sku.sku.name,
                    'price':str(order_sku.price),
                    'count':str(order_sku.count),
                    'default_image_url':order_sku.sku.default_image_url,
                    'comment':order_sku.comment,
                    'is_anonymous':order_sku.comment_is_anonymous,
                })
            #返回数据
            
            res=R.ok().data(**{
            'order_id':order_id,
            'uncomment_order_skus_list':uncomment_order_skus_list
            })
            
    def post(self,req):
        
        """上传sku评论数据
        """
        order_id=req.POST.get('order_id')
        order_sku_id=req.POST.get('order_sku_id')
        comment=req.POST.get('comment')
        is_anonymous=req.POST.get('is_anonymous')
        order,sku=None
        if not all([order_id,order_sku_id,comment,is_anonymous]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        try:
            order=Order.objects.get(order_id=order_id,status=ORDER_STATUS['UNCOMMENT'])
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        try:
            sku=SKU.objects.get(id=order_sku_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        #检查是否匿名评论 is_anonymous

        #保存评论
        OrderSku.objects.filter(order=order,sku=sku).update(
            comment=comment,
            is_anonymous=is_anonymous,
            is_commented=True
        )
        
        sku.comment_count+=1
        sku.goods.comment_count+=1
        sku.save()
        sku.goods.save()
        
        #如果该订单所有sku都已经完成评论,则该订单完成
        if OrderSku.objects.filter(order_id=order_id,is_commented=False).count()==0:
            order.update(status=ORDER_STATUS['FINISHED'])
        
        res=R.ok.data()
        
        return JsonResponse(res)
    
    
class SkuCommentView(View):
    """获取sku的评论信息
    """
    def get(self,req,sku_id):
        order_skus_list=OrderSku.objects.filter(sku_id=sku_id,is_commented=True)
        comment_list=[]
        
        for order_sku in order_skus_list:
            username=order_sku.order.user.username
            comment_list.append({
                'username':username,
                'comment':order_sku.comment
            })
            
        res=R.ok().data(**{
            'comment_list':comment_list
        })
        
        return JsonResponse(res)
            
# /orders/computation/
class OrderComputation(View):
        
    def get(self,req):
        pass
# /order/confirm/
class OrderConfirmView(View):
    
    def get(self,req):
        address=req.user.default_address

        redis_Cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        user_carts_key=Rediskey.USER_CARTS_KEY.format(user_id=req.user.id)
        
        user_redis_cart_info=redis_Cli.hgetall(user_carts_key)
        
        #结算
        total_count=0
        total_price=0
        
        skus=SKU.objects.in_bulk(list(user_redis_cart_info.keys()))
        
        order_info={}
        for sku in skus:
            if user_redis_cart_info[sku.id]['is_selected']:
                order_info[sku.id]={
                    'name':sku.name,
                    'count':user_redis_cart_info[sku.id]['count'],
                    'price':str(sku.sale_price),
                    'defalut_image_url':sku.default_image_url,
                    #及更多信息， 如折扣
                }
            total_count+=user_redis_cart_info[sku.id]['count']
            total_price+=user_redis_cart_info[sku.id]['count']*sku.sale_price
        
        order_info['total_count']=total_count
        order_info['total_price']=total_price
        
        res=R.ok().data(**{
         'order_info':order_info   
        })
        
        return JsonResponse(res)
        
            


            
 # /order/commit/
class OrderCommitView(View):
    
    def get(self,req):
        pass                
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    