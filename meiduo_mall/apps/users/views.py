from json import loads
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
from django_redis import get_redis_connection
import re
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.areas.models import Address


# Create your views here.
class UserCountView(View):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()

        return JsonResponse({"code": 0, "count": count, "errmsg": "ok"})


class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()

        return JsonResponse({"code": 0, "count": count, "errmsg": "ok"})


class RegisterView(View):
    def post(self, request):
        from django.contrib.auth import login


        # 接受请求
        try:
            body_str = request.body.decode()
            body_dict = loads(body_str)
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})

        # 获取数据
        username = body_dict.get('username')
        password = body_dict.get('password')
        password2 = body_dict.get('password2')
        mobile = body_dict.get('mobile')
        sms_code_cli = body_dict.get('sms_code')
        allow = body_dict.get('allow')
        redis_cli = get_redis_connection('code')
        sms_code_ser = redis_cli.get(mobile)

        # 验证数据
        if not all([username, password, password2, mobile, allow]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        if not re.match('[a-zA-Z_-]{5,20}', username):
            return JsonResponse({"code": 400, "errmsg": "用户名格式错误"})
        elif User.objects.filter(username=username).count() != 0:
            return JsonResponse({"code": 400, "errmsg": "用户名重复"})
        if not re.match(r'\d{8,20}', password):
            return JsonResponse({"code": 400, "errmsg": "密码格式错误"})
        if not password2 == password:
            return JsonResponse({"code": 400, "errmsg": "验证密码与密码不同"})
        if not re.match(r'1[3-9]\d{9}', mobile):
            return JsonResponse({"code": 400, "errmsg": "电话号码格式错误"})
        elif User.objects.filter(mobile=mobile).count() != 0:
            return JsonResponse({"code": 400, "errmsg": "电话号重复"})
        if not sms_code_ser:
            return JsonResponse({"code": 400, "errmsg": "短信验证码已过期"})
        elif sms_code_cli != sms_code_ser.decode():
            return JsonResponse({"code": 400, "errmsg": "短信验证码错误"})

        # 保存用户信息
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        
        # 实现状态保持
        login(request, user)

        return JsonResponse({"code": 0, "errmsg": "ok"})


class LoginView(View):
    def post(self, request):
        from django.contrib.auth import authenticate, login


        # 获取数据
        try:
            data = loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')

        # 验证数据
        if not all([username, password]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        # 判断用户名类型
        if re.match(r'1[3-9]\d{9}', username):
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        # 验证用户信息
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            return JsonResponse({"code": 400, "errmsg": "用户名或密码错误"})
        
        # 判断是否记住登录
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)

        # 返回响应
        response = JsonResponse({"code": 0, "errmsg": "ok"})
        response.set_cookie('username', username)

        return response


class LogoutView(View):
    def delete(self, request):
        from django.contrib.auth import logout


        logout(request)
        response = JsonResponse({"code": 0, "errmsg": "ok"})
        response.delete_cookie('username')

        return response


class CenterView(LoginRequiredMixin, View):
    # 重写了父类的dispatch方法
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"code": 400, "errmsg": "用户未登录"})
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        info_data = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }

        return JsonResponse({"code": 0, "errmsg": "ok", 'info_data': info_data})


class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        from apps.users.utils import generic_email_verify_token
        from celery_tasks.send_email.tasks import celery_send_email


        # 接受请求
        try:
            data = loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        # 获取数据
        email = data.get('email')
        # 验证数据
        if email is None:
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        result = re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email)
        if result is None:
            return JsonResponse({"code": 400, "errmsg": "邮箱格式错误"})

        # 保存邮箱地址
        user = request.user     # 获取用户信息
        # 判断用户邮箱是否已经存在
        if not user.email is None:
            pass
        elif user.email == email:
            pass
        else:
            user.email = email
            user.save()

        # 配置发送邮件信息
        subject = '美多商城激活邮件'        # 主题
        message = ''        # 内容
        from_email = '美多商城<youremail>'     # 发件人
        recipient_list = [email]      # 收件人列表
        token = generic_email_verify_token(user.id)         # 对token进行加密
        # 查询发送标记
        redis_cli = get_redis_connection("email")
        result = redis_cli.get(email)
        if result is None:
            # 发送激活邮件
            celery_send_email.delay(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, token=token)
            # 添加发送标记
            redis_cli.setex(email, 300, "1")

            # 返回响应
            return JsonResponse({"code": 0, "errmsg": "ok"})
        else:       # 重复发送
            # 返回响应
            return JsonResponse({"code": 400, "errmsg": "频繁发送邮件"})


class EmailVerifyView(View):
    def put(self, request):
        from apps.users.utils import checkout_email_verify_token


        # 获取数据
        token = request.GET.get('token')
        # 解密数据并验证
        user_id = checkout_email_verify_token(token)
        if user_id is None:
            return JsonResponse({"code": 400, "errmsg": "参数不全或错误"})
        # 查找用户
        user = User.objects.get(id=user_id)

        # 验证发送标记是否过期
        redis_cli = get_redis_connection("email")
        result = redis_cli.get(user.email)
        if result is None:
            return JsonResponse({"code": 400, "errmsg": "链接已过期"})
        else:
            # 修改数据
            user.email_active = True
            user.save()

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok"})


class AddressCreateView(LoginRequiredMixin, View):
    def post(self, request):
        # 接收数据
        try:
            data = loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        user = request.user
        # 验证数据
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return HttpResponseBadRequest('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return HttpResponseBadRequest('参数email有误')
        
        # 数据入库
        address = Address.objects.create(
                user = request.user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
        )

        # 转换数据
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        # 返回响应

        return JsonResponse({"code": 0, "errmsg": "ok", "address": address_dict})


class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 查询指定数据
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False)
        # 转换数据
        address_list = []
        for address in addresses:
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        # 返回响应
        default_id = request.user.default_address_id

        return JsonResponse({"code": 0, "errmsg": "ok", "addresses": address_list, 'default_address_id': default_id})
            

class UpdateDestoryAddressVIew(LoginRequiredMixin, View):
    """更新和删除用户地址"""


    def put(self, request, address_id):
        """更新地址"""
        # 获取数据 
        try:
            data = loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        receiver = data.get('receiver')
        province_id = data.get('province_id')
        city_id = data.get('city_id')
        district_id = data.get('district_id')
        place = data.get('place')
        mobile = data.get('mobile')
        tel = data.get('tel')
        email = data.get('email')
        user = request.user

        # 验证参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({"code": 400, "errmsg": "手机号格式错误"})
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({"code": 400, "errmsg": "tel格式错误"})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({"code": 400, "errmsg": "邮箱格式错误"})
            
        # 查询指定记录并更新
        try:
            Address.objects.filter(id=address_id, user=user, is_deleted=False).update(
                user = user,
                title = receiver,
                receiver = receiver,
                province_id = province_id,
                city_id = city_id,
                district_id = district_id,
                place = place,
                mobile = mobile,
                tel = tel,
                email = email
            )

        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "更新地址失败"})
        
        # 构建响应数据
        address = Address.objects.get(id=address_id, user=user, is_deleted=False)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 返回响应

        return JsonResponse({"code": 0, "errmsg": "ok", "address": address_dict})
    
    def delete(self, request, address_id):
        """删除地址"""
        # 查询指定数据并验证
        user = request.user
        address = Address.objects.get(user=user, id=address_id, is_deleted=False)
        if address is None:
            return JsonResponse({"code": 400, "errmsg": "该地址不存在"})
        
        # 删除数据(逻辑删除)
        address.is_deleted = True
        address.save()
        # 返回响应

        return JsonResponse({"code": 0, "errmsg": "ok"})


class DefaultAddressView(LoginRequiredMixin, View):
    """设置默认地址"""


    def put(self, request, address_id):
        # 查询指定数据并验证
        user = request.user
        address = Address.objects.get(user=user, id=address_id, is_deleted=False)
        if address is None:
            return JsonResponse({"code": 400, "errmsg": "该地址不存在"})
        # 将该地址设为默认
        user.default_address = address
        user.save()
        # 返回响应

        return JsonResponse({"code": 0, "errmsg": "ok"})


class UpdateTitleAddressView(LoginRequiredMixin, View):
    """修改地址标题"""


    def put(self, request, address_id):
        # 获取数据
        try:
            data = loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        title = data.get('title')
        user = request.user

        # 查询指定数据并验证
        if not re.match(r'^.{1,20}$', title):
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        address = Address.objects.get(user=user, id=address_id, is_deleted=False)
        if address is None:
            return JsonResponse({"code": 400, "errmsg": "该地址不存在"})
        # 修改地址标题
        address.title = title
        address.save()
        # 返回响应
        
        return JsonResponse({"code": 0, "errmsg": "ok"})


class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""


    def put(self, request):
        from django.contrib.auth import logout


        # 接受数据
        try:
            data = loads(request.body.decode())
        except Exception as e:
            return JsonResponse({"code": 400, "errmsg": "参数格式错误"})
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        new_password2 = data.get('new_password2')
        user = request.user

        # 验证参数
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({"code": 400, "errmsg": "参数不全"})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code':400,'errmsg':'密码最少8位,最长20位'})
        if new_password != new_password2:
            return JsonResponse({'code':400,'errmsg':'两次输入密码不一致'})
        result = user.check_password(old_password)
        if not result:
            return JsonResponse({'code':400,'errmsg':'原密码不正确'})
        
        # 修改密码
        user.set_password(new_password)
        user.save()
        # 清除状态保持信息
        logout(request)
        response = JsonResponse({'code':0,'errmsg':'ok'})
        response.delete_cookie('username')

        # 返回响应
        return JsonResponse({'code':0, 'errmsg':'ok'})


class UserBrowseHistory(LoginRequiredMixin, View):
    """用户浏览记录视图"""
    def post(self, request):
        from apps.goods.models import SKU
        from django_redis import get_redis_connection


        # 接收数据
        user = request.user
        data = loads(request.body.decode())
        sku_id = data.get('sku_id')

        # 验证数据
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return JsonResponse({"code": 400, "errmsg": "没有该商品"})

        # 链接redis
        redis_cli = get_redis_connection("history")
        # 去重
        redis_cli.lrem("history_%s"%user.id, 0, sku_id)
        # 添加浏览记录
        redis_cli.lpush("history_%s"%user.id, sku_id)
        # 修剪列表，使其只保留五条数据
        redis_cli.ltrim("history_%s"%user.id, 0, 4)

        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok"})
    
    def get(self, request):
        from apps.goods.models import SKU
        from django_redis import get_redis_connection


        # 获取历史记录
        redis_cli = get_redis_connection('history')
        id_list = redis_cli.lrange('history_%s'%request.user.id, 0, -1)

        # 将查询的数据转化json格式
        history_list = []
        for sku_id in id_list:
            sku = SKU.objects.get(id=sku_id)
            history_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        
        # 返回响应
        return JsonResponse({"code": 0, "errmsg": "ok", "skus": history_list})
