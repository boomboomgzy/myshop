import json

from myshop.utils.constants import rongLianYun_accId,rongLianYun_accToken,rongLianYun_appId,rongLianYun_tid,SMS_CODE_REDIS_EXPIERS
from ronglian_sms_sdk import SmsSDK



sdk=SmsSDK(rongLianYun_accId,rongLianYun_accToken,rongLianYun_appId)

def send_sms_code(mobile,sms_code):
    
    datas=(sms_code,int(SMS_CODE_REDIS_EXPIERS/60))
    sms_res=json.loads(sdk.sendMessage(rongLianYun_tid,mobile,datas))
    if sms_res.get('statusCode')=='000000':
        return True #发生成功
    else:
        return False
    
    
    

