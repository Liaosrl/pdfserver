import flask, os, sys,time,_thread,shutil,re
from threading import Thread
#from gevent.pywsgi import WSGIServer
from flask_dropzone import Dropzone
from flask import request,redirect,url_for,send_file,make_response,render_template,flash,abort,send_from_directory
from flask_bootstrap import Bootstrap
from pdftool2 import pdfproc
import base64,uuid

from form import LoginForm,SignupForm,FormatForm,EncryptForm,DecryptForm
from flask_wtf.csrf import CSRFProtect
from model import User,Anonymous 
from db import init_db, db_session
from sendemail import sendemail
from flask_login import login_user, login_required
from flask_login import LoginManager, current_user
from flask_login import logout_user

DOWNLOAD_EXPIRE_TIME=5
USERFILE_EXPIRE_TIME=15
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg','JPG','JPEG'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

basedir = os.path.abspath(os.path.dirname(__file__))
server = flask.Flask(__name__, static_folder='static',template_folder='template')
bootstrap = Bootstrap(server)
server.secret_key = os.urandom(24)
server.config['SECRET_KEY']=server.secret_key
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./pdftool_users.db'
server.config.update(dict(
    DEBUG=False,
    #SERVER_NAME = '0.0.0.0:80',
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = "pdftoolse6770@gmail.com",
    MAIL_PASSWORD = "******",
    MAIL_DEFAULT_SENDER = 'pdftoolse6770@gmail.com',
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
))

# use login manager to manage session
login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.session_protection = 'strong'
login_manager.login_view = 'index'
login_manager.init_app(app=server)

# csrf protection
csrf = CSRFProtect()
csrf.init_app(server)

#flask dropzone
dropzone = Dropzone()
dropzone.init_app(server)
server.config['DROPZONE_ENABLE_CSRF'] = True
server.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
server.config['DROPZONE_ALLOWED_FILE_TYPE'] = '.png, .jpg, .jpeg, .JPG, .pdf, .JPEG'
server.config['DROPZONE_UPLOAD_MULTIPLE'] = False
server.config['DROPZONE_PARALLEL_UPLOADS']=1
server.config['DROPZONE_MAX_FILES']=10
server.config['DROPZONE_MAX_FILE_SIZE']=10

@server.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@server.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',title='404 Not found', value='Sorry, we cannot find the things you want.'), 404

@server.errorhandler(500)
def internal_error(e):
    return render_template('error.html',title='Sorry for the inconvinience', value='We encounter some unexpected problems.'), 500

@server.route('/signup',methods=['post'])
def signup():
    form=SignupForm()
    try:
        if form.validate_on_submit():
            user_name = request.form.get('username', None)
            password = request.form.get('password', None)
            email = request.form.get('email', None)
            if not checkusername(user_name):
                return render_template('error.html',title='Signup Fail', value='Illegal username')
            if not checkemail(email):
                return render_template('error.html',title='Signup Fail', value='Wrong email format')
            user = User(user_name)
            user.email=email
            if not user.exists():
                token = user.generate_confirmation_token()
                user.password = password
                sendemail(user.email, 'confirm Your Account','confirm', user=user, token=token)
                return redirect(url_for('index'))
                #if ret:
                    #return redirect(url_for('index'))
                #else:
                    #return render_template('error.html',title='Signup Fail', value='Fail to send email')
            else:
                return render_template('error.html',title='Signup Fail', value='User or email exists')
        else:
            return render_template('error.html',title='Signup Fail', value='Please fill all part')
    except:
        return render_template('error.html',title='Signup Fail', value='Oops, we encounter some problems, please contact us for details.')

@server.route('/resendemail')
@login_required
def resendemail():
    try:
        if current_user.is_anonymous or current_user.confirmed:
            return redirect(url_for('index'))
        else:
            token = current_user.generate_confirmation_token()
            sendemail(current_user.email, 'confirm Your Account','confirm',user=current_user,token=token)
            return redirect(url_for('index'))
        #return redirect(url_for('index'))
    except:
        return render_template('error.html',title='Signup Fail', value='Fail to send email')

@server.route('/confirm/<token>')
def confirm(token):
    try:
        if current_user.is_authenticated and current_user.confirmed:
            return redirect(url_for('index'))
        elif User.confirm(token):
            #print('email confirmed')
            return redirect(url_for('index'))
        else:
            print('email confirm fail')
            return render_template('error.html',title='confirm Fail', value='Fail to confirm email')
    except:
        return render_template('error.html',title='confirm Fail', value='Oops, we encounter some problems, please contact us for details.')

@server.route('/login',methods=['post'])
def login():
    form = LoginForm()
    try:
        if form.validate_on_submit():
            user_name = request.form.get('username', None)
            password = request.form.get('password', None)
            remember_me = request.form.get('remember_me', False)
            if not checkusername(user_name):
                return render_template('error.html',title='Login Fail', value='Illegal username')
            user = User(user_name)
            if user.verify_password(password):
                login_user(user,remember=remember_me)
                return redirect(url_for('index'))
            else:
                return render_template('error.html',title='Login Fail', value='Wrong username or password')
        else:
            return render_template('error.html',title='Login Fail', value='Please fill all part')
    except:
        #print(e)
        return render_template('error.html',title='login Fail', value='Oops, we encounter some problems, please contact us for details.')

@server.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@server.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(basedir, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')

@server.route('/', methods=['get'])
def index():
    pageid=str(uuid.uuid4())
    pageid=base64.b64encode(pageid.encode('ascii'))
    #loginform = LoginForm()
    #signupform=SignupForm()
    #encryptform = EncryptForm()
    #decryptform = DecryptForm()
    #return render_template('homepage.html',pageid=pageid,loginform=loginform,signupform=signupform,encryptform=encryptform,decryptform=decryptform)
    return render_template('homepage.html',pageid=pageid)

@server.route('/upload/<func>/<path:pageid>', methods=['post'])
def upload(func,pageid):
    try:
        pageid=base64.b64decode(pageid)
        pageid=pageid.decode('ascii')

        uploaded_file = request.files["file"]

        t = time.strftime('%Y%m%d%H%M%S')
        serviceid=pageid+"-"+func
        file_dir = os.path.join(basedir,"userfiles", serviceid)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        with open(os.path.join(file_dir,"0.txt"),"w") as f:
            f.write(t)
        
        if uploaded_file:
            back=uploaded_file.filename.split(".")
            if len(back)>=2 and back[-1] in ALLOWED_EXTENSIONS:
                filelist=os.listdir(file_dir)
                fileord=len(filelist)
                new_fname = str(fileord)+"."+back[-1]
                uploaded_file.save(os.path.join(file_dir, new_fname)) 
                return "OK",200
            else:
                return "unsupported file", 400
        else:
            return "file update fail", 400
    except:
        return "file update fail", 400

@server.route('/pdfop/<func>/<path:pageid>', methods=['get','post'])
def preproc(func,pageid):
    #try:
        pageid=base64.b64decode(pageid)
        pageid=pageid.decode('ascii')
        
        if func.startswith('split'):
            serviceid=pageid+"-"+"split"
        else:
            serviceid=pageid+"-"+func
        file_dir = os.path.join(basedir,"userfiles", serviceid)

        if not os.path.exists(file_dir):
            return render_template('error.html', title='Processing err', value='No supported file uploaded')

        if func == "encrypt":
            form = EncryptForm()
            if form.validate_on_submit():
                userpassword=request.form.get('userpassword')
                ownerpassword=request.form.get('ownerpassword')
                path=pdfproc(file_dir,func,ownerpass=ownerpassword,userpass=userpassword)
            else:
                return render_template('error.html', title='Processing err', value='Please fill both password part')

        elif func == "decrypt":
            form = DecryptForm()
            if form.validate_on_submit():
                password=request.form.get('password')
                path=pdfproc(file_dir,func,password=password)
            else:
                return render_template('error.html', title='Processing err', value='Please fill password part')

        elif func== "img2pdf" or func=="addimg":
            form = FormatForm()
            if form.validate_on_submit():
                if request.form.get('letter')=="on":
                    letter=True
                else:
                    letter=False
                path=pdfproc(file_dir,func,letter=letter)
            else:
                return render_template('error.html', title='Processing err', value='Please fill the checkbox')
        else: 
            path=pdfproc(file_dir,func)
        
        ret="file="+path
        if not path.startswith("error:"):
            cleanprocess = Thread(target=autoclean,args=(path,DOWNLOAD_EXPIRE_TIME))
            cleanprocess.start()
            ret=base64.urlsafe_b64encode(ret.encode('ascii'))
            return redirect(url_for('success',filename=ret))
        else:
            return render_template('error.html', title='Processing error', value=path.split(":")[1].lstrip())
    #except:
        #return render_template('error.html',title='Processing error', value='We encounter some unexpected problems.')

@server.route('/success/<path:filename>', methods=['get'])
def success(filename):
    return render_template('download.html',filename=filename)

@server.route('/download/<path:filename>', methods=['get'])
def download(filename):
    try:
        filename=base64.urlsafe_b64decode(filename)
        filename=filename.decode('ascii')
        realname=filename.lstrip('file=')
        path,name=os.path.split(realname)
        if os.path.exists(realname):
            response = make_response(send_file(realname, as_attachment=True))
            response.headers["Content-Disposition"] = "attachment; filename={}".format(name)
            return response
        else:
            abort(404)
    except:
        abort(404)

def checkemail(email):
    splitted=email.split("@")
    if len(splitted)!=2 or splitted[0]=="" or splitted[1]=="":
        return False
    else:
        splitted=splitted[1].split(".")
        if len(splitted)!=2 or splitted[0]=="" or splitted[1]=="":
            return False
        else:
            return True

def checkusername(username):
    if not re.search(u'^[_a-zA-Z0-9\u4e00-\u9fa5]+$', username):
        return False
    else:
        return True

def autoclean(file,lifetime):
    time.sleep(lifetime*60)
    folder,_=os.path.split(file)
    folder,_=os.path.split(folder)
    if os.path.exists(folder):
        shutil.rmtree(folder)
        #print("deleted")
    return 0

def clean(lifetime):
    while True:
        path=os.path.join(basedir,"userfiles")
        folders= os.listdir(path)
        #print(files)
        for folder in folders:
            if os.path.exists(os.path.join(path,folder,'0.txt')):
                with open(os.path.join(path,folder,'0.txt')) as f:
                    timestamp=int(f.readline())
                t = int(time.strftime('%Y%m%d%H%M%S'))
                if t-timestamp>lifetime*100:
                    shutil.rmtree(os.path.join(path,folder))
        time.sleep(lifetime*60)

if __name__=="__main__":
    _thread.start_new_thread(clean,(USERFILE_EXPIRE_TIME,))
    init_db()
    server.config['DEBUG']=True
    server.run(host='127.0.0.1',port='8000',threaded=True)