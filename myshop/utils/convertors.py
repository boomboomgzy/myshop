import imp
from django.urls import converters
import logging
from django.conf import settings
logger=logging.getLogger(settings.LOGGER_NAME)

class UsernameConverter:
    regex='[a-zA-Z0-9_-]{3,20}'
    
    def to_python(self,value):
        #logger.info('getname: {}'.format(value))
        return value