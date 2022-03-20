from django.conf import settings
from celery_tasks.main import celery_app
from .ronglianyun import send_sms_code
import logging

logger=logging.getLogger(settings.LOGGER_NAME)

# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
# send_res: bool  true为成功，false为失败
@celery_app.task(bind=True,name='celery_send_sms_code',retry_backoff=3)
def celery_send_sms_code(self,mobile,sms_code):
    try:
        send_res=send_sms_code(mobile,sms_code)    
    except Exception as e:
        logger.error(e)
        raise self.retry(exc=e,max_retries=3)        

    if not send_res:
        logger.info('ronglianyun respond: {}'.format('短信发送失败'))
        raise self.retry(exc=Exception('短信发生失败'),max_retries=3) 
    return send_res
             
        