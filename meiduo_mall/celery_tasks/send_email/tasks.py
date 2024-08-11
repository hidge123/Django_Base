from django.core.mail import send_mail
from celery_tasks.main import app


@app.task(name='send_email')
def celery_send_email(subject, message, from_email, recipient_list, token):
    # 组织激活邮件链接
    verify_url = "http://www.meiduo.site:8080/success_verify_email.html?token=%s" % token
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (recipient_list[0], verify_url, verify_url)
    send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list, html_message=html_message)
