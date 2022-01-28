from django.core.mail import send_mail
from myshop.celery_tasks.main import celery_app
import logging
from django.conf import settings


logger=logging.getLogger(settings.LOGGER_NAME)

@celery_app.task(bind=True,name='celery_send_verify_email',retry_backoff=3)
def celery_send_verify_email(self,email,verify_url):
    subject='商城邮箱验证'
    html_message='<P>你的邮箱为：{} 。请点击以下链接进行激活：</p>'\
                 '<p><a href="{}">{}</a></p>'.format(email,verify_url,verify_url)
                 
    try:
        send_mail(
            subject=subject,
            html_message=html_message,
            from_email=settings.EMAIL_FROM,
            recipient_list=[email],
        )
    except Exception as e:
        logger.error(e)
        raise self.retry(exc=e,max_retries=3)
        
        