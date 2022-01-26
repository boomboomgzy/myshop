import json

from sqlalchemy import false, true
from myshop.utils.random import random_str
from myshop.utils.constants import rongLianYun_accId,rongLianYun_accToken,rongLianYun_appId,rongLianYun_tid,SMS_CODE_REDIS_EXPIERS
from ronglian_sms_sdk import SmsSDK


#测试手机号
test_mobile='13360236820'

sdk=SmsSDK(rongLianYun_accId,rongLianYun_accToken,rongLianYun_appId)

def send_sms_code(mobile,sms_code):
    
    datas=(sms_code,SMS_CODE_REDIS_EXPIERS)
    
    sms_res=json.load(sdk.sendMessage(rongLianYun_tid,mobile,datas))
    if sms_res.get('statusCode')=='000000':
        return true #发生成功
    else:
        return false
    
    
    

