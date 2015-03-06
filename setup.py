from cx_Freeze import setup,Executable

includefiles = [ 'arcadia_admin/', 'config.py', 'arcadia_admin.py']
includes = ['jinja2.ext', 'flask_sqlalchemy._compat']
excludes = []
packages = ['arcadia_admin', 'email']

setup(
name = 'arcadia_admin',
version = '0.1',
description = 'arcadia admin',
author = 'Me',
author_email = 'me@me.com',
options = {'build_exe': {'packages':packages,'includes':includes,'excludes':excludes,'include_files':includefiles}}, 
executables = [Executable('arcadia_admin.py')], requires=['flask', 'requests', 'wtforms', 'SQLAlchemy']
)
