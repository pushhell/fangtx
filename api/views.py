from uuid import uuid1

from django.core.cache import caches
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from api.helpers import MyAuthentication
from api.serializers import DistrictSerializer, HouseTypeSerializer, EstateSerializer
from common.models import District, HouseType, Estate, User, UserToken

# 省级行政区域数据量本身并不大而且数据不会变
# 这样的数据就适合直接放到缓存中而且设置为永不超时
# 第1种做法：通过api_view装饰器来注册REST数据接口
from common.utils import to_md5_hex, gen_mobile_code, send_short_message


@api_view(['GET'])
@throttle_classes([])
@cache_page(timeout=None, cache='api')
def provinces(request):
    queryset = District.objects.filter(parent__isnull=True)
    serializer = DistrictSerializer(queryset, many=True)
    return Response(serializer.data)
    # return JsonResponse(serializer.data, safe=False)
    # return HttpResponse(json.dumps(serializer.data), content_type='application/json')


@api_view(['GET'])
@throttle_classes([])
@cache_page(timeout=300, cache='api')
def cities(request, provid):
    queryset = District.objects.filter(parent__distid=provid)
    serializer = DistrictSerializer(queryset, many=True)
    return Response(serializer.data)


# 第2种做法：继承APIView及其子类（可能需要重写对应的方法）
# class HouseTypeApiView(ListAPIView, RetrieveAPIView):
#     queryset = HouseType.objects.all()
#     serializer_class = HouseTypeSerializer
#
#     @cache_response(timeout=None, cache='api')
#     def get(self, request, pk=None, *args, **kwargs):
#         return RetrieveAPIView.get(self, request, *args, **kwargs) if pk \
#             else ListAPIView.get(self, request, *args, **kwargs)


# 第三种做法：继承ModelViewSet并通过Router注册路由
class HouseTypeViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    queryset = HouseType.objects.all()
    serializer_class = HouseTypeSerializer
    # 取消配置文件中配置的默认分页方式
    pagination_class = None


class EstateViewSet(CacheResponseMixin, ModelViewSet):
    # 通过queryset指定如何获取数据（资源）
    queryset = Estate.objects.all().select_related('district').prefetch_related('agents')
    # 通过serializer_class指定如何序列化数据
    serializer_class = EstateSerializer
    # 通过pagination_class指定如何分页（覆盖默认的设置）
    # pagination_class = MyPageNumberPagination
    # 通过filter_backends指定如何提供筛选（覆盖默认的设置）
    # filter_backends = (DjangoFilterBackend, OrderingFilter)
    # 指定根据哪些字段进行数据筛选
    filter_fields = ('district', 'name')
    # 指定根据哪些字段对数据进行排序
    ordering_fields = ('hot', )
    # 通过throttle_classes可以指定自定义的限流策略（覆盖默认的设置）
    # 如果希望自定义限流类可以继承BaseThrottle或其子类并重写allow_requset和wait方法
    # throttle_classes = ()
    # AA - Authenication / Authorization
    # 如果要对接口的访问加以限制就需要使用认证（合法用户？）和授权（执行操作？）
    authentication_classes = (MyAuthentication, )
    # permission_classes = (MyPermission, )


@api_view(['GET'])
def mobile_code(request, tel):
    code_str = gen_mobile_code()
    request.session['mobile_code'] = code_str
    # 将用户手机号放入缓存并通过中间件来限制120秒内不能重复发送短信
    caches['api'].set(tel, code_str, 120)
    # 下面的函数是通过调用三方平台实现短信服务 调用三方平台最显著的问题是时间不可预期
    # 假如第三方平台出现故障 那么代码就会在下面阻塞 相当于因为三方平台故障导致自己的系统崩溃
    # 所以将来执行调用三方平台（时间不可预估）的任务或者执行耗费时间较长的任务
    # 必须以异步的方式 保证代码不会因为这样的任务而阻塞 - 使用消息队列
    # 此处相当于是消息的生产者
    # 可以通过Celery启动消息的消费者来处理这条消息
    # celery -A fangtx worker
    send_short_message.delay(tel, code_str)
    return Response({'code': 20000, 'message': '短信验证码已经发送'})


@api_view(['POST'])
def login(request):
    resp_dict = {'code': 30000, 'message': '用户登录成功'}
    username = request.POST['username']
    password = request.POST['password']
    try:
        password = to_md5_hex(password)
        user = User.objects.filter(username=username, password=password).only('realname').first()
        if user:
            resp_dict['userid'] = user.userid
            # 通过UUID算法生成用户令牌（稍后用户认证身份的标识）
            token = uuid1().hex
            resp_dict['token'] = token
            # 创建或更新保存用户令牌的表（将新令牌写入表中）
            UserToken.objects.update_or_create(user=user, defaults={'token': token})
        else:
            resp_dict['code'] = '30001'
            resp_dict['message'] = '用户名或密码错误'
    except:
        resp_dict['code'] = '30002'
        resp_dict['message'] = '服务器升级维护中请稍后尝试登录'
    return Response(resp_dict)
