from functools import wraps
from myshop.utils.enums import StatusCodeEnum
from myshop.utils.exceptions import BusinessException

def login_required_json(view_func):
    """
    判断用户是否登录的装饰器，并返回json
    :param view_func: 被装饰的视图函数
    :return: json、view_func
    """

    # 恢复view_func的名字和文档
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        # 如果用户未登录，返回json数据
        if not request.user.is_authenticated:
            raise BusinessException(StatusCodeEnum.SESSION_ERR)
        else:
            # 如果用户登录，进入到view_func中
            return view_func(request, *args, **kwargs)

    return wrapper


class LoginRequiredJSONMixin(object):
    """验证用户是否登陆并返回json的扩展类"""

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required_json(view)
