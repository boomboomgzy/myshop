import random

def random_str(count):
    """
    生成固定长度的字符串，由字母和数字1-9组成

    Args:
        count (int): 字符串的位数
    """
    s=''
    e='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz123456789'
    for i in range(0,count):
        j=random.randint(0,len(e)-1)
        s+=e[j]    
        
    return s

        