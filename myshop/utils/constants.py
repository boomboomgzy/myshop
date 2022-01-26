#图形验证码过期时间 单位：S
IMG_CODE_REDIS_EXPIRES=180

#容联云短信验证码过期时间 单位：m
SMS_CODE_REDIS_EXPIERS=5

#容联云短信发送间隔时间 单位: m
SMS_CODE_REDIS_INTERVAL=1

#容联云
rongLianYun_accId='8aaf07087e7b9872017e865a4c020155'
rongLianYun_accToken='82e0c70222324753a0c4d96e2f695257'
rongLianYun_appId='8aaf07087e7b9872017e865a4d16015b'
rongLianYun_tid='1'

    #redis key
class Rediskey(object):
    
    IMG_CODE_KEY='myshop_img_code_{uuid}'
    
    SMS_CODE_KEY='myshop_sms_code_{mobile}'
    
    SMS_SEND_FLAG_KEY='myshop_sms_send_flag_{mobile}'
    