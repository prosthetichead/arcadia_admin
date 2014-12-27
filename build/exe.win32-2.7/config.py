import os, sys

## Findout if we are frozen or not.
if getattr(sys, 'frozen', False):
	#we are frozen so let it go.
	basedir = os.path.dirname(sys.executable)
else:
	basedir = os.path.dirname(__file__)

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'arcadia.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')