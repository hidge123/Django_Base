# 使用itsdangerous对openid进行加密和解密
from itsdangerous import TimedSerializer as Serializer, BadData, SignatureExpired, BadTimeSignature
from meiduo_mall.settings import SECRET_KEY


# 加密
def generic_openid(openid):
    s = Serializer(secret_key=SECRET_KEY)
    openid = s.dumps(openid)

    return openid.decode()

# 解密
def check_openid(openid):
    s = Serializer(secret_key=SECRET_KEY)
    try:
        openid = s.loads(openid)
    except (BadData, SignatureExpired, BadTimeSignature):
        return None
    else:
        return openid
