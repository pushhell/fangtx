from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission

from common.models import UserToken


class MyPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'size'
    max_page_size = 50


class MyAuthentication(BaseAuthentication):
    """自定义用户身份认证类"""

    def authenticate(self, request):
        try:
            token = request.GET['token'] or request.POST['token']
            user_token = UserToken.objects.filter(token=token).first()
            if user_token:
                return user_token.user, user_token
            else:
                raise AuthenticationFailed('请提供有效的用户身份标识')
        except KeyError:
            raise AuthenticationFailed('请提供有效的用户身份标识')


# 用户 - 角色 - 权限 （三者都是多对多关系）
# 如果用户和角色是多对一关系或者用户和权限之间也有中间实体（中间表）
# 那么只需要一重循环直接获取用户权限再检查是否跟当前请求匹配即可
class MyPermission(BasePermission):
    """自定义授权类（RBAC - 基于角色的访问控制）"""

    def has_permission(self, request, view):
        method = request.method
        path = request.path
        for role in request.user.roles.all():
            for priv in role.privileges.all():
                if priv.method == method and priv.path == path:
                    return True
        return False

