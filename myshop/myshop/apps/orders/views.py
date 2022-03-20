from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from myshop.apps.goods.models import SKU
from myshop.apps.users.models import Address
from myshop.apps.orders.models import Order, OrderSku
from django.conf import settings
import logging
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from myshop.utils.constants import ORDER_STATUS, HtmlTemplate, Rediskey,ORDER_FREIGHT,ORDER_PAY_METHOD,ORDER_SHOW_LIMIT
from django_redis import get_redis_connection
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
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
                    'default_image_url':order_sku.sku.default_image.url,
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
class OrderComputation(LoginRequiredMixin,View):
        
    def get(self,req):
        user=req.user
        
        try:
            addresses=Address.objects.filter(user=user,is_deleted=False)
        except Exception as e:
            addresses=None
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        
        user_redis_cart_count_dic=redis_cli.hgetall(Rediskey.USER_CARTS_COUNT_KEY.format(user_id=user.id))
        user_redis_cart_select_dic=redis_cli.hgetall(Rediskey.USER_CARTS_SELECT_KEY.format(user_id=user.id))
        #构造购物车信息数据
        cart_info_dic={}
        for sku_id,count in user_redis_cart_count_dic.items():
            cart_info_dic[int(sku_id)]={
            'count':count.decode()
        }
        for sku_id,selected in user_redis_cart_select_dic.items():
            cart_info_dic[int(sku_id)]['selected']=selected.decode()
        #初始数据
        total_count=0
        total_amount=Decimal(0.00)
        #取出选中的sku
        selected_sku_id=[]
        for sku_id in cart_info_dic.keys():
            if cart_info_dic[sku_id]['selected']=='True':
                selected_sku_id.append(sku_id)
                
        skus=SKU.objects.filter(id__in=selected_sku_id)
        for sku in skus:
            total_count+=1
            total_amount+=int(cart_info_dic[sku.id]['count'])*sku.sale_price
        
        freight=Decimal(ORDER_FREIGHT)
        
        #json化
        addresses_list=[]
        skus_list=[]
        for address in addresses:
            address_json={
                'id':address.id,
                'receiver':address.receiver,
                'province':address.province.name,
                'city':address.city.name,
                'district':address.district.name,
                'mobile':address.mobile
            }
            addresses_list.append(address_json)
        for sku in skus:
            sku_json={
                'name':sku.name,
                'price':str(sku.sale_price),
                'count':cart_info_dic[sku.id]['count'],
                'amount':str(int(cart_info_dic[sku.id]['count'])*sku.sale_price),
                'default_image':sku.default_image.url
            }
            skus_list.append(sku_json)            
            
        res={
            'addresses':addresses_list,
            'skus':skus_list,
            'total_count':total_count,
            'total_amount':total_amount,
            'freight':freight,
            'payment_amount':total_amount+freight           
        }
        return render(req,HtmlTemplate.ORDER_PLACE_HTML,res)
        
        
# /orders/success/
class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功"""

    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, HtmlTemplate.ORDER_SUCCESS_HTML, context)


            
 # /orders/commit/
class OrderCommitView(View):
    
    def save_order(self,user,order_id,address,pay_method):
        if pay_method== ORDER_PAY_METHOD['ALIPAY']:
            pay_status=ORDER_STATUS['UNPAID']
        else:
            pay_status=ORDER_STATUS['UNSEND']
            
        order = Order.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=Decimal(0.00),
            send_price=Decimal(ORDER_FREIGHT),
            pay_method=pay_method,
            status=pay_status
        )
        
        redis_cli=get_redis_connection(settings.CARTS_CACHE_ALIAS)
        user_redis_cart_count_info_key=Rediskey.USER_CARTS_COUNT_KEY.format(user_id=user.id)
        user_redis_cart_count_info=redis_cli.hgetall(user_redis_cart_count_info_key)
        user_redis_cart_select_info_key=Rediskey.USER_CARTS_SELECT_KEY.format(user_id=user.id)
        user_redis_cart_select_info=redis_cli.hgetall(user_redis_cart_select_info_key)
        #构造购物车信息数据
        cart_info_dic={}
        for sku_id,count in user_redis_cart_count_info.items():
            cart_info_dic[int(sku_id)]={
                'count':count.decode()
            }
        for sku_id,selected in user_redis_cart_select_info.items():
            cart_info_dic[int(sku_id)]['selected']=selected.decode()
        
        cart_dict={}
        
        for sku_id in cart_info_dic.keys():
            if cart_info_dic[sku_id]['selected']:
                cart_dict[sku_id]=cart_info_dic[sku_id]['count']
        
        sku_ids=cart_dict.keys()
        
        for sku_id in sku_ids:
            
            while True:
                sku=SKU.objects.get(id=sku_id)
                
                origin_stock=sku.stock
                origin_sale_count=sku.sale_count
                buy_count=int(cart_dict[sku_id])
                
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
        order.total_amount+=Decimal(ORDER_FREIGHT)
        order.save()
        p1=redis_cli.pipeline()
        redis_cli.hdel(user_redis_cart_select_info_key,*sku_ids)
        redis_cli.hdel(user_redis_cart_count_info_key,*sku_ids)
        p1.execute()
        
    def post(self,req):
        #订单提交
        json_dict=json.loads(req.body.decode())
        address_id=json_dict.get('address_id')
        pay_method=json_dict.get('pay_method')
        
        if not all([address_id,pay_method]):
            raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)
        
        try:
            address=Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
        
        pay_method_v_list=[]
        for key in ORDER_PAY_METHOD.keys():
            pay_method_v_list.append(ORDER_PAY_METHOD[key])
        
        if pay_method not in pay_method_v_list:
            raise BusinessException(StatusCodeEnum.PARAM_ERR)
    
        user=req.user
        order_id=timezone.localtime().strftime('%Y%m%d%H%M%S')+('%09d' % user.id)
        
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
            
# /orders/info/<pagenum>
class UserOrderInfoView(View):
    
    def get(self,req,page_num):
        user=req.user
        orders=user.orders.all().order_by('-create_time')
        
        for order in orders:
            order.status_name=Order.ORDER_STATU_CHOICES[order.status][1]
            order.pay_method_name=Order.PAY_METHOD_CHOICES[order.pay_method-1][1]
            order.sku_list=[]
            for order_sku in order.skus.all():
                sku=order_sku.sku
                sku.count=order_sku.count
                sku.amount=order_sku.price*order_sku.count
                order.sku_list.append(sku)
        try:
            pat=Paginator(orders,ORDER_SHOW_LIMIT)
            page_orders=pat.page(page_num)
            total_page=pat.num_pages
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        res={
            'page_orders':page_orders,
            'total_page':total_page,
            'page_num':page_num,
        }
        
        return render(req,HtmlTemplate.USER_CENTER_ORDER,res)
        

            
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    