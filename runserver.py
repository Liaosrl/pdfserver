from gevent.pywsgi import WSGIServer
import pdfserver_auth
from pdfserver_auth import server,clean
import _thread
import logging 
from logging.handlers import RotatingFileHandler
from db import init_db

infolog='./infolog.log'

log_format=logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
info_handler = RotatingFileHandler(infolog, mode='a', 
                                    maxBytes=1024*1024, 
                                    backupCount=2, 
                                    encoding=None, 
                                    delay=0) 
info_handler.setFormatter(log_format) 

info_log=logging.getLogger('root') 
info_log.addHandler(info_handler)
info_log.setLevel(logging.INFO) 

_thread.start_new_thread(clean,(pdfserver_auth.USERFILE_EXPIRE_TIME,))
init_db()
http_server = WSGIServer(('0.0.0.0', 80), server,log=info_log)
http_server.serve_forever()
