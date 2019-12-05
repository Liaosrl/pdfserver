from flask import Flask
from flask_mail import Mail, Message
from flask import render_template, current_app
from threading import Thread



def async_send_mail(mail,app,msg):
    with app.app_context():
        mail.send(message=msg)

def sendemail(to, subject, template, **kwargs):
    try:
        app = current_app._get_current_object()
        mail=Mail(app)
        msg = Message(subject,sender=app.config["MAIL_DEFAULT_SENDER"],recipients=[to])
        #msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        send = Thread(target=async_send_mail,args=(mail,app,msg))
        send.start()
        #mail.send(msg) #launch
        return True
    except Exception as e:
        print(e)
        return False