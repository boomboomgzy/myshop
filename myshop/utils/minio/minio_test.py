# 引入MinIO包。
import sys
import os
import django
sys.path.append('G:\\vscode\webproject\myshop')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myshop.settings")  # MB：项目名称
django.setup()
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
from django.conf import settings
import logging
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException
logger=logging.getLogger(settings.LOGGER_NAME)

    
# 使用endpoint、access key和secret key来初始化minioClient对象。
minioClient = Minio(settings.MINIO_URL,
                    access_key=settings.MINIO_ACCESSKEY,
                    secret_key=settings.MINIO_SECRETKEY,
                    secure=False)
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
        minioClient.fput_object(settings.MINIO_BUCKETNAME,save_filename,originname)
    except Exception as e:
        logger.error(e)
    else:
        try:   
            pass
            #url=minioClient.presigned_get_object(settings.MINIO_BUCKETNAME,save_filename,MINIO_URL_EXPIERS)
        except Exception as e:
            logger.error(e)
        else:
            #return url 
            pass 



# 调用make_bucket来创建一个存储桶。
try:
       minioClient.make_bucket(settings.MINIO_BUCKETNAME, location="us-east-1")
except BucketAlreadyOwnedByYou as err:
       print(err)
except BucketAlreadyExists as err:
       print(err)
except ResponseError as err:
       raise
try:
    #object_name 是远程Minio服务器的bucket下的相对文件路径
    #file_path 是待上传文件的文件路径
    minioClient.fput_object(settings.MINIO_BUCKETNAME, '/jpeg/03.jpeg', 'G:/vscode/webproject/myshop/myshop/utils/minio/02.jpeg')
except Exception as err:
        print(err)