from decimal import Decimal
from django.http import JsonResponse
from django.views import View
from myshop.apps import orders
from myshop.apps.goods.models import SKU
from myshop.apps.users.models import Address
from myshop.apps.orders.models import Order, OrderSku
from django.conf import settings
import logging
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.constants import ORDER_STATUS, Rediskey,ORDER_FREIGHT,ORDER_PAY_METHOD,ORDER_SHOW_LIMIT
from django_redis import get_redis_connection
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator

logger=logging.getLogger(settings.LOGGER_NAME)

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
        user=req.user
        
        try:
            addresses=Address.objects.filter(user=user,is_deleted=False)
        except Exception as e:
            addresses=None
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        
        user_carts_key=Rediskey.USER_CARTS_KEY.format(user_id=user.id)
        
        redis_cart_dic=redis_cli.hget(user_carts_key)
        
        cart={}
        #初始数据
        total_count=0
        total_amount=0.00
        
        for sku_id in redis_cart_dic:
            if redis_cart_dic[sku_id]['selected']:
                cart[sku_id]=redis_cart_dic[sku_id]['count']
        
        skus=SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            total_count+=1
            total_amount+=cart[sku.id]['count']*sku.sale_price
        
        freight=Decimal(ORDER_FREIGHT)
        
        res=R.ok().data(**{
            'address':addresses,
            'skus':skus,
            'total_count':total_count,
            'total_amount':total_amount,
            'freight':freight,
            'pay_amount':total_amount+freight           
        })
        
        return JsonResponse(res)
        
        
            


            
 # /orders/commit/
class OrderCommitView(View):
    
    def save_order(self,user,order_id,address,pay_method):
        if pay_method== ORDER_PAY_METHOD['ALIPAY'] or pay_method==ORDER_PAY_METHOD['CASH']:
            pay_status=ORDER_STATUS['UNPAID']
        else:
            pay_status=ORDER_STATUS['UNSEND']
            
        order = Order.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=0.00,
            freight=ORDER_FREIGHT,
            pay_method=pay_method,
            status=pay_status
        )
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        user_carts_key=Rediskey.USER_CARTS_KEY.format(user_id=user.id)
        
        
        redis_cart=redis_cli.hget(user_carts_key)
        cart_dict={}
        
        for sku in redis_cart:
            if sku['selected']:
                cart_dict[sku]=sku['count']
        
        sku_ids=cart_dict.keys()
        
        for sku_id in sku_ids:
            
            while True:
                sku=SKU.objects.get(id=sku_id)
                
                origin_stock=sku.stock
                origin_sale_count=sku.sale_count
                
                buy_count=cart_dict[sku_id]['count']
                
                if buy_count>origin_stock:
                    raise BusinessException(StatusCodeEnum.STOCK_ERR)
                
                new_stock=origin_stock-buy_count
                new_sale_count=origin_sale_count+buy_count
                result=SKU.objects.filter(id=sku_id,stock=origin_stock).update(stock=new_stock,sale_count=new_sale_count)
                
                if not result:
                    continue
                
                sku.goods.sale_count+=buy_count
                sku.save()
                
                OrderSku.objects.create(
                    order=order,
                    sku=sku,
                    count=buy_count,
                    price=sku.sale_price,
                )

                order.total_count+=1
                order.total_amount+=buy_count*sku.sale_price
                
                break;
        order.total_amount+=ORDER_FREIGHT
        order.save()
        
        p1=redis_cli.pipeline()
        redis_cli.hdel(user_carts_key,*sku_ids)
        p1.execute()
        
    def post(self,req):
        #订单提交
        address_id=req.POST.get('address_id')
        pay_method=req.POST.get('pay_method')
        
        if not all([address_id,pay_method]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        try:
            address=Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        pay_method_v_list=[]
        for key in ORDER_PAY_METHOD:
            pay_method_v_list+=ORDER_PAY_METHOD[key]
        
        if pay_method not in pay_method_v_list:
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
    
        user=req.user
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S')+user.id
        
        with transaction.atomic():
            save_id=transaction.savepoint()
            
            try:
                self.save_order(user,order_id,address,pay_method)
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise BusinessException(StatusCodeEnum.DB_ERR)
            
            transaction.savepoint_commit(save_id)
            
            res=R.ok().data(**{
                'order_id':order_id
            })
            
            return JsonResponse(res)
            
# /orders/info/
class UserOrderInfoView(View):
    
    def get(self,req,page_num):
        user=req.user
        orders=user.orders.all().order_by('-create_time')
        
        for order in orders:
            order.status_name=Order.ORDER_STATU_CHOICES[order.status][1]
            order.pay_method_name=Order.PAY_METHOD_CHOICES[order.pay_method-1][1]

        
        try:
            pat=Paginator(orders,ORDER_SHOW_LIMIT)
            page_orders=pat.page(page_num)
            total_page=pat.num_pages
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        res=R.ok().data(**{
            'page_orders':page_orders,
            'total_page':total_page,
            'page_num':page_num,
        })
        
        return JsonResponse(res)
        

            
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    