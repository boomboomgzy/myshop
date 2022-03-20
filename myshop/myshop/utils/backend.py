from django.contrib.auth.backends import ModelBackend
from myshop.apps.users.models import User
from django.db.models import Q

class UserNameAndEmailBackend(ModelBackend):
    def authenticate(self, req, username=None,password=None,**kw):
        try:
            user=User.objects.get(Q(mobile=password) | Q(username=username))
        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None
        

        