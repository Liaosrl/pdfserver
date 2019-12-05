from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin,AnonymousUserMixin
from sqlalchemy import Column, Integer, String,Boolean
from db import Base,db_session
import uuid

class User(UserMixin,Base):
    __tablename__ = 'users'
    id = Column(String(120), primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(120), unique=True)
    email =Column(String(120), unique=True)
    confirmed=Column(Boolean, unique=False)

    def __init__(self, username):
        self.username = username
        self.password_hash = self.get_password_hash()
        self.id,self.email,self.confirmed=self.get_info()
    def __repr__(self):
        return '<User %r>' % (self.username)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        try:
            self.password_hash = generate_password_hash(password)
            db_session.add(self)
            db_session.commit()
        except:
            print("add user fail")
        
    def verify_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def get_password_hash(self):
        try:
            u = User.query.filter(User.username==self.username).first()
            if u:
                return u.password_hash
            else:
                return None
        except Exception as e:
            print("get passwordhash fail",e)
            return None

    def get_info(self):
        """get user id from db, if not exist, it will
        generate a uuid for the user.
        """
        if self.username is not None:
            try:
                u = User.query.filter(User.username==self.username).first()
                if u:
                    return u.id,u.email,u.confirmed
                else:
                    return str(uuid.uuid4()),None,False
            except Exception as e:
                return str(uuid.uuid4()),None,False


    def generate_confirmation_token(self,expiration=7200):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id})

    @staticmethod
    def confirm(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
            id=data.get('confirm')
            u=User.query.filter(User.id==id).first()
            if u:
                u.confirmed=True
                db_session.add(u)
                db_session.commit()
                return True
            else:
                return False
        except:
            print("confirm fail")
            return False

    def exists(self):
        if self.username is not None and self.email is not None:
            try:
                u = User.query.filter(User.username==self.username).all()
                e = User.query.filter(User.username==self.email).all()
                if not u and not e:
                    return False
                else:
                    return True
            except Exception as e:
                print("exists fail")
                return True

    @staticmethod
    def get(user_id):
        """try to return user_id corresponding User object.
        This method is used by load_user callback function
        """
        try:
            u = User.query.filter(User.id==user_id).first()
            user=User(u.username)
            user.id=u.id
            return user
        except:
            print("call back fail")
            return None
        return None

class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = "temp"
        self.id = str(uuid.uuid4())
    def __repr__(self):
        return '<User %r>' % (self.username)