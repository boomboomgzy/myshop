from django.http import JsonResponse
from myshop.apps.payment.models import Payment
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.result import R
from django.shortcuts import render
from django.conf import settings
import logging
from alipay import AliPay
from django.views import View
from myshop.apps.orders.models import Order
from myshop.settings import ALIPAY_RETURN_URL
from myshop.utils.constants import ORDER_STATUS


logger=logging.getLogger(settings.LOGGER_NAME)

#创建alipay客户端
def create_alipaycli():
    with open(settings.ALIPAY_PUBLIC_KEY_PATH,mode='r') as f:
        alipay_public_key=f.read()
    with open(settings.APP_PRIVATE_KEY_PATH,mode='r') as f:
        app_private_key=f.read()
        
    alipay=AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,
        alipay_public_key_string=alipay_public_key,
        app_private_key_string=app_private_key,
        sign_type='RSA2',
        debug=settings.ALIPAY_DEBUG
    )
    
    return alipay

# /payment/<order_id>
class PaymentView(View):
    #支付订单
    def get(self,req,order_id):
        """

        Args:
            order_id : 订单号
        """
        try:
            order=Order.objects.get(pk=order_id)
        except Exception as e:
            logger.error(e)
            raise BusinessException(StatusCodeEnum.DB_ERR)
        
        alipay=create_alipaycli()
        
        res_order_info=alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject='myshop'+str(order_id),
            return_url=settings.ALIPAY_RETURN_URL
        )
        
        alipay_url=settings.ALIPAY_URL+'?'+res_order_info
        
        res=R.ok().data(**{
            'alipay_url':alipay_url
        })
        
        return JsonResponse(res)
        
        
# /payment/status
class PaymentStatusView(View):
    #查询并更新订单状态
    def get(self,req):
        #获取参数词典
        query_dict=req.GET.dict()
        sign=query_dict.pop('sign')
        
        alipay=create_alipaycli()
        #校验，确保该请求是支付宝发给我们
        success=alipay.verify(query_dict,sign)
        
        if success:
            order_id=query_dict['out_trade_no']
            trade_id=query_dict['trade_no']
            
            #保存支付信息
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            ) 
            
            #修改订单状态
            Order.objects.filter(pk=order_id).update(status=ORDER_STATUS['UNCOMMENT'])
            
            #支付成功 响应信息
        else:
            raise BusinessException(StatusCodeEnum.BAD_REQ_ERR)    