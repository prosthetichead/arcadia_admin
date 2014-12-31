import os, sys

## Findout if we are frozen or not.
if getattr(sys, 'frozen', False):
	#we are frozen so let it go.
	basedir = os.path.dirname(sys.executable)
else:
	basedir = os.path.dirname(__file__)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-might-guess-if-you-are-lucky'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'arcadia.db')
UPLOAD_FOLDER = os.path.join(basedir, 'arcadia_admin/uploads')