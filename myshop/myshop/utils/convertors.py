import imp
from django.urls import converters
import logging
from django.conf import settings

logger=logging.getLogger(settings.LOGGER_NAME)

class UsernameConverter:
    regex='[a-zA-Z0-9_-]{3,20}'
    
    def to_python(self,value):
        logger.info('getname: {}'.format(value))
        return value

        
class MobileConverter:
    regex='1(3\d|4[5-9]|5[0-35-9]|6[2567]|7[0-8]|8\d|9[0-35-9])\d{8}'
    
    def to_python(self,value):
        logger.info('getmobile: {}'.format(value))
        return value