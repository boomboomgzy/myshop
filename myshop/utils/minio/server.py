from xmlrpc.client import boolean
from minio import Minio
import logging
from django.conf import settings
from myshop.utils.constants import minio_AccessKey,minio_SecretKey,minio_Bucket,MINIO_URL_EXPIERS
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
logger=logging.getLogger(settings.LOGGER_NAME)

minio_cli=Minio(settings.MINIO_URL,
                access_key=minio_AccessKey,
                secret_key=minio_SecretKey,
                secure=True)

#创建文件夹
try:
    exist=minio_cli.bucket_exists(minio_Bucket)
    if not exist:
        minio_cli.make_bucket(minio_Bucket)
except Exception as e:
    logger.error(e)
    
#生成随机文件名

def getRandomFileName(originname,prefix):
    """
    :parma originname:原文件名
    :parma prefix:bucket内的路径
    """
    extend_name=originname.split('.')[1]
    uuid=str(uuid.uuid1())
    if prefix is not None:
        return prefix+'/'+uuid+extend_name
    else:
        return uuid+extend_name
    
#文件上传
def fileUpload(originname,prefix):
    if originname is None :
        raise BusinessException(StatusCodeEnum.NECESSARY_PARAM_ERR)   
    save_filename=getRandomFileName(originname,prefix)
    try:
        minio_cli.fput_object(minio_Bucket,save_filename,originname)
    except Exception as e:
        logger.error(e)
    else:
        try:   
            url=minio_cli.presigned_get_object(minio_Bucket,save_filename,MINIO_URL_EXPIERS)
        except Exception as e:
            logger.error(e)
        else:
            return url  

    
