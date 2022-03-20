from django import http
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import View
from django_redis import get_redis_connection
from myshop.utils.exceptions import BusinessException
from myshop.utils.my_random import random_str
from myshop.utils.enums import StatusCodeEnum
from .libs.captcha import captcha
from myshop.utils.result import R
from myshop.settings import VERIFY_CODE_CACHE_ALIAS
from celery_tasks.sms.task import celery_send_sms_code
from myshop.utils.constants import SMS_CODE_REDIS_INTERVAL, Rediskey,IMG_CODE_REDIS_EXPIRES,rongLianYun_accId,rongLianYun_accToken,rongLianYun_appId,rongLianYun_tid,SMS_CODE_REDIS_EXPIERS
import logging 

logger=logging.getLogger(settings.LOGGER_NAME)
# image_codes/<uuid>  图片验证码
class ImageCodeView(View):
    
    def get(self,req,uuid):
        img_code,img=captcha.generate_captcha()
        redis_cli=get_redis_connection(VERIFY_CODE_CACHE_ALIAS)
        img_code_key=Rediskey.IMG_CODE_KEY.format(uuid=uuid)
        redis_cli.setex(img_code_key,IMG_CODE_REDIS_EXPIRES,img_code)
        
        return http.HttpResponse(img,content_type='image/jpg')

# sms_code/<mobile> 短信验证码  
class SmsCodeView(View):
    
    def get(self,req,mobile):
        img_code=req.GET.get('image_code')
        uuid=req.GET.get('uuid')
        
        if not all ([img_code,uuid]):
            res=R.set_result(StatusCodeEnum.NECESSARY_PARAM_ERR).data()
            return http.JsonResponse(res)

        redis_cli=get_redis_connection(VERIFY_CODE_CACHE_ALIAS)    

        #检查用户是否频繁发送验证码
        sms_send_flag_key=Rediskey.SMS_SEND_FLAG_KEY.format(mobile=mobile)
        send_flag=redis_cli.get(sms_send_flag_key)
        if send_flag:
            res=R.set_result(StatusCodeEnum.THROTTLING_ERR).data()

        #获取图片验证码
        img_code_key=Rediskey.IMG_CODE_KEY.format(uuid=uuid)
        img_code_correct=redis_cli.get(img_code_key)
        
        #判断redis中该图片验证码是否存在
        if img_code_correct is None:
            raise BusinessException(StatusCodeEnum.IMAGE_CODE_ERR)  
           
        img_code_correct=img_code_correct.decode()
        #用户使用了该图片验证码，则从redis中删除
        redis_cli.delete(img_code_key)
        #如果图片验证码正确，则可以发送短信验证码
        if img_code.lower()==img_code_correct.lower():
            sms_code=random_str(6)
            sms_code_key=Rediskey.SMS_CODE_KEY.format(mobile=mobile)
            
            #使用redis管道，批量传输redis指令
            p=redis_cli.pipeline()
            p.setex(sms_code_key,SMS_CODE_REDIS_EXPIERS,sms_code)
            p.setex(sms_send_flag_key,SMS_CODE_REDIS_INTERVAL,1)
            p.execute()
            #使用celery异步发送信息
            celery_send_sms_code(mobile,sms_code)
            
            res=R.ok().data()
            return JsonResponse(res)
        else:
            res=R.set_result(StatusCodeEnum.IMAGE_CODE_ERR).data()
            return JsonResponse(res)               
        

        