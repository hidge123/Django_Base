from itsdangerous import TimedSerializer as Serialier, BadData, SignatureExpired, BadTimeSignature
from meiduo_mall.settings import SECRET_KEY


def generic_email_verify_token(user_id):
    # 创建实例
    s = Serialier(secret_key=SECRET_KEY)
    # 加密数据
    data = s.dumps(user_id)
    
    return data
