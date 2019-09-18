# -*- coding: utf-8 -*-

from flask import request, Flask, json,jsonify, g ,render_template
from flask_httpauth import HTTPTokenAuth
import time, datetime
from threading import Thread
from flask_mail import Mail, Message
import os

app = Flask(__name__, template_folder='./templ')
auth = HTTPTokenAuth(scheme='Token')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# set config var
app.config.from_pyfile('config.conf')
tokens = app.config['TOKENS_LIST']

mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# async send mail
def send_mail(to, subject, template, **kwargs):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.html = render_template(template , **kwargs)
    thread = Thread(target=send_async_email, args=[app, msg])
    thread.start()
    return thread

@auth.verify_token
def verify_token(token):
    g.user = None
    if token in tokens:
        g.user = tokens[token]
        return True
    return False

@app.route('/mail', methods=['POST'])
@auth.login_required
def post_mail():
    dhostname = request.form['dhostname']
    mip = request.form['mip']
    dtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(request.form['dtime'])))
    dip = request.form['dip']
    duser = request.form['duser']
    print(request.form.to_dict())
    context={
        'dhostname': dhostname,
        'mip': mip,
        'dtime': dtime,
        'dip': dip,
        'duser': duser
    }
    receiver = app.config['MAIL_RECEIVER']
    title = '主机 {0} 登入信息'.format(dhostname)
    send_mail(receiver, title , 'mail.html', **context)
    datenow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    recognize_info = {'info': 'POST request accept', 'date': datenow}
    return jsonify(recognize_info), 200

@app.route('/')
def index():
    html=('<br/> '
        'POST http://hostname_or_IP:9090/mail with token <br/>'
        'data format: <br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp; mip &nbsp;&nbsp;    # login system IP <br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp; dip &nbsp;&nbsp;    # remote used IP  <br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp; dhostname &nbsp;&nbsp; # login hostname <br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp; duser &nbsp;&nbsp;  # login used username<br/>'
        '&nbsp;&nbsp;&nbsp;&nbsp; dtime &nbsp;&nbsp;  # login timestamp(ms)<br/>'
    )
    return html

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=9090)
