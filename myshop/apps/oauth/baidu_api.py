from aiohttp import request
from django.conf import settings
from itsdangerous import BadData, TimedJSONWebSignatureSerializer
import requests
import logging
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
from myshop.utils.constants import BAIDU_MYSHOP_TOKEN_EXPIRES
logger=logging.getLogger(settings.LOGGER_NAME)


def get_baidu_access_token(code):
    
    url='https://openapi.baidu.com/oauth/2.0/token'
    query_parma={
        'grant_type':'authorization_code',
        'code':code,
        'client_id':settings.BAIDU_API_KEY,
        'client_secret':settings.BAIDU_SECRET_KEY,
        'redirect_uri':settings.BAIDU_REDIRECT_URI,
    }
    baidu_res=requests.get(url,query_parma).json()
    if baidu_res.get['error'] is not None:
        logger.error(baidu_res)
        raise BusinessException(StatusCodeEnum.SERVER_ERR)
    
    access_token=baidu_res.get['access_token']
    settings.BAIDU_REFRESH_TOKEN=baidu_res.get['fresh_token']
    
    return access_token
    

def get_baidu_user_openid(access_token):
    
    url='https://openapi.baidu.com/rest/2.0/passport/users/getInfo'
    query_param={
        'access_token':access_token
    }
    baidu_res=requests.get(url,query_param).json()
    
    if baidu_res.get['error_code'] is not None:
        logger.error(baidu_res)
        raise BusinessException(StatusCodeEnum.SERVER_ERR)
    
    baidu_openid=baidu_res.get('openid')
    baidu_username=baidu_res.get('username')
    logger.info('login user:')
    logger.info({
        'baidu_openid':baidu_openid,
        'baidu_username':baidu_username
    })
    
    return baidu_openid


def encrypt_baidu_openid(openid):
    from itsdangerous import TimedJSONWebSignatureSerializer
    
    data={'baidu_openid':openid}
    serializer=TimedJSONWebSignatureSerializer(settings.ITSDANGEROUS_SECRET_KEY,BAIDU_MYSHOP_TOKEN_EXPIRES)
    myshop_token=serializer.dumps(data)
    return myshop_token.decode()

def decrypt_myshop_token(myshop_token):
    serializer=TimedJSONWebSignatureSerializer(settings.ITSDANGEROUS_SECRET_KEY)
    try:
        data=serializer.loads(myshop_token)
    except BadData:
        return None
    else:
        return data.get('baidu_openid')










