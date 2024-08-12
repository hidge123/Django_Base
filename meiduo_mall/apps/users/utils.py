from itsdangerous import TimedSerializer as Serialier, BadData, SignatureExpired, BadTimeSignature
from meiduo_mall.settings import SECRET_KEY


def generic_email_verify_token(user_id):
    # 创建实例
    s = Serialier(secret_key=SECRET_KEY)
    # 加密数据
    data = s.dumps(user_id)
    
    return data

def checkout_email_verify_token(token):
    # 创建实例
    s = Serialier(secret_key=SECRET_KEY)
    # 解密数据
    try:
        data = s.loads(token)
    except (BadData, SignatureExpired, BadTimeSignature):
        return None
    
    return data